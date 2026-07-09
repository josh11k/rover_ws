"""Hardware-agnostic fake mono-camera node.

This is the diagram's "mono_cam_node" ("acquires data from mono cam"), the
entry point of the LED-detection branch (mono_cam_node -> led_detector_node
-> position_rover_node). Same fake-hardware convention as elsewhere in this
workspace (FakeUsbInterface, FakeStereoCameraInterface): a small interface
class stands in for the real camera SDK, swappable later without touching
the ROS2 node around it.

Setup (see ARCHITECTURE.md): this mono-cam is mounted on the same fixed
mast as the rest of the perception module and observes a single, separate
rover driving around it. Since one panel of LEDs can only be seen from
roughly the hemisphere it faces, the rover carries **three** LED panels --
roof, left, right -- covering most viewing angles as it turns (front/back
are deliberately left uncovered for now, see chat). Each panel:

  - has the same shape: 3 LEDs at the corners of an isosceles triangle
    (panel_base_m / panel_leg_m) plus a 4th LED on one of the two equal
    legs (panel_extra_led_fraction along it). Unlike a symmetric shape
    (square, equilateral triangle), this has NO rotational or mirror
    symmetry -- every one of the 4 LEDs is geometrically unique, so
    position_rover_node can always figure out which is which from
    geometry alone, no per-LED color-coding needed.
  - has its own solid color (roof=green, left=red, right=blue), so
    led_detector_node / position_rover_node can tell *which panel* they're
    looking at without needing to see more than one at once.

Placeholder geometry throughout (panel shape+size, mounting positions/
normals on the rover body) -- replace with real measurements once the
rover's physical LED mounts are finalized. position_rover_node's DEFAULTS
must mirror panel_base_m/panel_leg_m/panel_extra_led_fraction and the
mount offsets/normals here exactly, or the fake scenario won't validate
correctly -- there is no shared source of truth for these yet (same
caveat as the stereo/lidar shared-plane constants).

Self-occlusion is simplified: a panel is only "visible" (LEDs rendered) if
its outward normal, after the rover's current yaw rotation, points at
least roughly toward the camera (dot product against the panel-to-camera
direction above visibility_dot_threshold). No actual rover-body geometry is
modeled -- each panel is treated as if it alone determines its own
visibility, good enough for a placeholder scene.

Real hardware: Arducam B0497 (Sony IMX678 sensor, USB3.0, UVC-compliant --
confirms the choice below of the generic ROS2 `v4l2_camera` driver over a
vendor-specific wrapper, no special driver needed):

    /mono_cam/image_raw    sensor_msgs/Image, encoding "rgb8"
    /mono_cam/camera_info  sensor_msgs/CameraInfo

v4l2_camera publishes unnamespaced topics (/image_raw, /camera_info) by
default -- launching it inside a `mono_cam` namespace (or remapping) gets
you these exact topic names, so swapping to real hardware later is: remove
this node from the launch file, launch v4l2_camera_node in that namespace
instead (set its `output_encoding` parameter to "rgb8" -- the sensor's
native format is YUY2, v4l2_camera converts). No downstream node needs to
change.

Two real-hardware quirks worth remembering once position_rover_node exists:
the lens is manual-focus, fixed at the factory to 3m-infinity -- anything
closer will be blurry, which matters if the rover can get closer than that
to the mast. And the sensor only has 3 fixed USB3.0 modes (3840x2160
@15fps, 1920x1080 @60fps, 1280x720 @90fps); this node defaults to
1920x1080 at a more Jetson-friendly 30fps (comfortably inside that mode's
60fps ceiling), not the native max.

Frame: mono_cam_optical_frame, REP-103 optical convention (Z forward, X
right, Y down) -- same convention used for the stereo camera.
"""

import math

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image, CameraInfo


DEFAULTS = {
    "image_topic": "/mono_cam/image_raw",
    "camera_info_topic": "/mono_cam/camera_info",
    "frame_id": "mono_cam_optical_frame",

    # 1920x1080 is one of the B0497's 3 native USB3.0 modes (see module
    # docstring); 30fps is a deliberately conservative choice (native max
    # for this mode is 60fps) to leave Jetson headroom for the rest of the
    # pipeline.
    "width": 1920,
    "height": 1080,
    "fps": 30.0,

    # Synthetic pinhole intrinsics, derived from the B0497 datasheet's
    # stated FOV (100 deg diagonal / 88 deg H / 72 deg V) via the pinhole
    # approximation fx = (width/2) / tan(fov_h/2) at the resolution above.
    # Wide-angle lenses like this one have real distortion the pinhole
    # model ignores -- replace with the real calibrated values (checkerboard
    # calibration) once hardware is available.
    "fx": 994.0,
    "fy": 743.0,
    "cx": 959.5,
    "cy": 539.5,

    # Shared LED-panel shape (all 3 panels use this same asymmetric
    # geometry -- see module docstring): isosceles triangle (2 legs of
    # panel_leg_m, base of panel_base_m) + a 4th LED at
    # panel_extra_led_fraction along ONE leg (0 = at the base corner,
    # 1 = at the apex). MUST match position_rover_node's DEFAULTS.
    "panel_base_m": 0.20,
    "panel_leg_m": 0.25,
    "panel_extra_led_fraction": 0.5,

    # Per-panel solid colors -- lets position_rover_node tell panels apart
    # without seeing more than one at a time.
    "panel_roof_color_r": 60, "panel_roof_color_g": 255, "panel_roof_color_b": 80,
    "panel_left_color_r": 255, "panel_left_color_g": 60, "panel_left_color_b": 60,
    "panel_right_color_r": 60, "panel_right_color_g": 120, "panel_right_color_b": 255,

    # Placeholder panel mounting, relative to the rover's own center/height
    # (before the rover's yaw rotation is applied -- see get_frame()).
    # MUST match position_rover_node's panel extrinsics DEFAULTS.
    "roof_height_offset_m": 0.20,
    "side_offset_m": 0.15,
    "side_height_offset_m": 0.05,

    # Self-occlusion cutoff (see module docstring): panel normal . direction
    # to camera must exceed this to be considered visible. ~0.15 -> panel
    # normal within ~81 degrees of pointing at the camera.
    "visibility_dot_threshold": 0.15,

    # Apparent blob radius (pixels) at 1m distance; actual radius scales
    # as 1/distance (perspective), clamped to this range.
    "led_apparent_radius_px_at_1m": 20.0,
    "min_led_radius_px": 2.0,
    "max_led_radius_px": 40.0,

    # Rover motion, simulated directly in the camera's optical frame
    # (no mast_link roundtrip needed for a synthetic scene): distance and
    # lateral position each oscillate on their own period (different
    # periods -> a more organic, non-repeating path), plus a slow yaw
    # rotation of the whole rover body (and everything mounted on it).
    "rover_center_distance_m": 3.0,
    "rover_distance_amplitude_m": 1.5,
    "rover_distance_period_s": 20.0,
    "rover_lateral_amplitude_m": 2.0,
    "rover_lateral_period_s": 14.0,
    "rover_height_m": 0.3,
    "rover_yaw_period_s": 11.0,

    "background_noise_std": 5.0,
}


def _build_panel_local_points(base_m: float, leg_m: float, extra_fraction: float) -> np.ndarray:
    """The shared 4-LED panel shape, in the panel's own 2D (u, v) plane
    (v=0 is the base, v>0 towards the apex): base-left, base-right, apex,
    and the extra LED on the base-left -> apex leg. See module docstring.
    """
    half_base = base_m / 2.0
    apex_height = math.sqrt(max(leg_m ** 2 - half_base ** 2, 1e-9))

    base_left = np.array([-half_base, 0.0])
    base_right = np.array([half_base, 0.0])
    apex = np.array([0.0, apex_height])
    extra = base_left + extra_fraction * (apex - base_left)

    return np.array([base_left, base_right, apex, extra])  # (4, 2)


class FakeMonoCameraInterface:
    """Stand-in for a real camera SDK / v4l2 capture loop.

    Generates a synthetic RGB8 frame each call to get_frame(t): a noisy dark
    background plus the rover's 3 LED panels (roof/left/right), each
    projected via a pinhole model as the rover moves and turns, with panels
    fading in/out of visibility depending on which way the rover is facing.
    Swapping to real hardware later means replacing only this class (and
    ideally just launching v4l2_camera instead of this whole node).
    """

    def __init__(
        self, width, height, fx, fy, cx, cy,
        panel_base_m, panel_leg_m, panel_extra_led_fraction,
        roof_color, left_color, right_color,
        roof_height_offset_m, side_offset_m, side_height_offset_m,
        visibility_dot_threshold,
        rover_center_distance_m, rover_distance_amplitude_m,
        rover_distance_period_s, rover_lateral_amplitude_m,
        rover_lateral_period_s, rover_height_m, rover_yaw_period_s,
        led_apparent_radius_px_at_1m, min_led_radius_px, max_led_radius_px,
        background_noise_std,
    ):
        self.width = width
        self.height = height
        self.fx = fx
        self.fy = fy
        self.cx = cx
        self.cy = cy

        self.rover_center_distance_m = rover_center_distance_m
        self.rover_distance_amplitude_m = rover_distance_amplitude_m
        self.rover_distance_period_s = max(rover_distance_period_s, 1e-3)
        self.rover_lateral_amplitude_m = rover_lateral_amplitude_m
        self.rover_lateral_period_s = max(rover_lateral_period_s, 1e-3)
        self.rover_height_m = rover_height_m
        self.rover_yaw_period_s = max(rover_yaw_period_s, 1e-3)

        self.led_apparent_radius_px_at_1m = led_apparent_radius_px_at_1m
        self.min_led_radius_px = min_led_radius_px
        self.max_led_radius_px = max_led_radius_px
        self.visibility_dot_threshold = visibility_dot_threshold

        panel_local_uv = _build_panel_local_points(
            panel_base_m, panel_leg_m, panel_extra_led_fraction
        )

        # Each panel: local (u,v) points embedded into the rover's own
        # unyawed 3D frame via mount_offset + u*right_axis + v*up_axis. The
        # outward normal is NOT chosen independently -- it's always
        # normal = right_axis x up_axis, so that [right_axis, up_axis,
        # normal] forms a proper (determinant +1) rotation matrix from
        # panel-local to rover-local. This matters: position_rover_node
        # reuses these exact same right_axis/up_axis/normal triples as the
        # panel's mounting *rotation* to compose a solved panel pose back
        # into a rover-center pose -- an improper (mirrored) basis would
        # silently produce a wrong/flipped rover pose. MUST match
        # position_rover_node's panel extrinsics DEFAULTS exactly.
        self._panels = [
            {
                "name": "roof",
                "color": roof_color,
                "mount_offset": np.array([0.0, roof_height_offset_m, 0.0]),
                "right_axis": np.array([1.0, 0.0, 0.0]),
                "up_axis": np.array([0.0, 0.0, -1.0]),
                "normal": np.array([0.0, 1.0, 0.0]),
            },
            {
                "name": "left",
                "color": left_color,
                "mount_offset": np.array([-side_offset_m, side_height_offset_m, 0.0]),
                "right_axis": np.array([0.0, 0.0, 1.0]),
                "up_axis": np.array([0.0, 1.0, 0.0]),
                "normal": np.array([-1.0, 0.0, 0.0]),
            },
            {
                "name": "right",
                "color": right_color,
                "mount_offset": np.array([side_offset_m, side_height_offset_m, 0.0]),
                "right_axis": np.array([0.0, 0.0, -1.0]),
                "up_axis": np.array([0.0, 1.0, 0.0]),
                "normal": np.array([1.0, 0.0, 0.0]),
            },
        ]
        for panel in self._panels:
            # local_points: (4, 3) -- the panel's 4 LEDs embedded in the
            # rover's unyawed 3D frame, still relative to mount_offset.
            panel["local_points"] = (
                panel_local_uv[:, 0:1] * panel["right_axis"]
                + panel_local_uv[:, 1:2] * panel["up_axis"]
            )

        # Static noisy background, generated once (fixed seed -> repeatable
        # test scenes) and reused every frame instead of re-randomizing at
        # full frame rate.
        rng = np.random.default_rng(seed=42)
        noise = rng.normal(20.0, background_noise_std, size=(height, width, 1))
        self._background = np.clip(noise, 0, 255).astype(np.uint8).repeat(3, axis=2)

        # Precompute the pixel grid once for vectorized blob rendering.
        vs, us = np.mgrid[0:height, 0:width]
        self._us = us.astype(np.float32)
        self._vs = vs.astype(np.float32)

    @staticmethod
    def _yaw(vec3: np.ndarray, cos_t: float, sin_t: float) -> np.ndarray:
        """Rotate about the vertical (Y) axis: mixes x/z, leaves y alone --
        same convention as the rover's own body yaw.
        """
        x, y, z = vec3
        return np.array([x * cos_t - z * sin_t, y, x * sin_t + z * cos_t])

    def get_frame(self, t: float) -> np.ndarray:
        """Return a (height, width, 3) uint8 RGB frame for elapsed time t."""

        frame = self._background.copy()

        distance_omega = 2.0 * math.pi / self.rover_distance_period_s
        lateral_omega = 2.0 * math.pi / self.rover_lateral_period_s
        yaw_omega = 2.0 * math.pi / self.rover_yaw_period_s

        center_z = (
            self.rover_center_distance_m
            + self.rover_distance_amplitude_m * math.sin(distance_omega * t)
        )
        center_z = max(center_z, 0.3)  # never let the rover reach the camera
        center_x = self.rover_lateral_amplitude_m * math.sin(lateral_omega * t)
        center_y = self.rover_height_m
        center = np.array([center_x, center_y, center_z])

        theta = yaw_omega * t
        cos_t, sin_t = math.cos(theta), math.sin(theta)

        for panel in self._panels:
            panel_center_unyawed = panel["mount_offset"]
            panel_center = self._yaw(panel_center_unyawed, cos_t, sin_t) + center
            normal_yawed = self._yaw(panel["normal"], cos_t, sin_t)

            # Visibility: does this panel's normal point roughly toward the
            # camera (at the origin)? See module docstring.
            to_camera = -panel_center
            to_camera_norm = to_camera / max(np.linalg.norm(to_camera), 1e-6)
            visible = float(np.dot(normal_yawed, to_camera_norm)) > self.visibility_dot_threshold

            if not visible:
                continue

            for local_pt in panel["local_points"]:
                point_unyawed = panel["mount_offset"] + local_pt
                x, y, z = self._yaw(point_unyawed, cos_t, sin_t) + center

                if z <= 0.05:
                    continue  # behind/at the camera -- not visible

                u = self.cx + self.fx * x / z
                v = self.cy + self.fy * y / z

                radius_px = float(np.clip(
                    self.led_apparent_radius_px_at_1m / z,
                    self.min_led_radius_px, self.max_led_radius_px,
                ))

                dist2 = (self._us - u) ** 2 + (self._vs - v) ** 2
                mask = dist2 <= (radius_px ** 2)
                frame[mask] = panel["color"]

        return frame


class FakeMonoCameraNode(Node):

    def __init__(self):
        super().__init__("fake_mono_camera_node")

        self._declare_parameters()
        self._load_parameters()

        self.interface = FakeMonoCameraInterface(
            width=self.width,
            height=self.height,
            fx=self.fx,
            fy=self.fy,
            cx=self.cx,
            cy=self.cy,
            panel_base_m=self.panel_base_m,
            panel_leg_m=self.panel_leg_m,
            panel_extra_led_fraction=self.panel_extra_led_fraction,
            roof_color=(self.panel_roof_color_r, self.panel_roof_color_g, self.panel_roof_color_b),
            left_color=(self.panel_left_color_r, self.panel_left_color_g, self.panel_left_color_b),
            right_color=(self.panel_right_color_r, self.panel_right_color_g, self.panel_right_color_b),
            roof_height_offset_m=self.roof_height_offset_m,
            side_offset_m=self.side_offset_m,
            side_height_offset_m=self.side_height_offset_m,
            visibility_dot_threshold=self.visibility_dot_threshold,
            rover_center_distance_m=self.rover_center_distance_m,
            rover_distance_amplitude_m=self.rover_distance_amplitude_m,
            rover_distance_period_s=self.rover_distance_period_s,
            rover_lateral_amplitude_m=self.rover_lateral_amplitude_m,
            rover_lateral_period_s=self.rover_lateral_period_s,
            rover_height_m=self.rover_height_m,
            rover_yaw_period_s=self.rover_yaw_period_s,
            led_apparent_radius_px_at_1m=self.led_apparent_radius_px_at_1m,
            min_led_radius_px=self.min_led_radius_px,
            max_led_radius_px=self.max_led_radius_px,
            background_noise_std=self.background_noise_std,
        )

        self.image_pub = self.create_publisher(
            Image,
            self.image_topic,
            qos_profile_sensor_data,
        )

        self.camera_info_pub = self.create_publisher(
            CameraInfo,
            self.camera_info_topic,
            qos_profile_sensor_data,
        )

        self.camera_info_msg = self._build_camera_info()
        self._start_time = self.get_clock().now()

        period = 1.0 / self.fps
        self.timer = self.create_timer(period, self.timer_callback)

        self.get_logger().info(
            f"Fake mono camera started: {self.width}x{self.height} "
            f"@ {self.fps} FPS, simulating 3 LED panels (roof/left/right) "
            f"at ~{self.rover_center_distance_m}m, publishing to "
            f"{self.image_topic}"
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def _build_camera_info(self) -> CameraInfo:
        info = CameraInfo()
        info.width = self.width
        info.height = self.height
        info.distortion_model = "plumb_bob"
        info.d = [0.0, 0.0, 0.0, 0.0, 0.0]
        info.k = [
            self.fx, 0.0, self.cx,
            0.0, self.fy, self.cy,
            0.0, 0.0, 1.0,
        ]
        info.r = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        info.p = [
            self.fx, 0.0, self.cx, 0.0,
            0.0, self.fy, self.cy, 0.0,
            0.0, 0.0, 1.0, 0.0,
        ]
        return info

    def timer_callback(self):
        elapsed = (self.get_clock().now() - self._start_time).nanoseconds * 1e-9
        frame = self.interface.get_frame(elapsed)
        stamp = self.get_clock().now().to_msg()

        image_msg = Image()
        image_msg.header.stamp = stamp
        image_msg.header.frame_id = self.frame_id
        image_msg.height = self.height
        image_msg.width = self.width
        image_msg.encoding = "rgb8"
        image_msg.is_bigendian = 0
        image_msg.step = self.width * 3
        image_msg.data = frame.tobytes()
        self.image_pub.publish(image_msg)

        self.camera_info_msg.header.stamp = stamp
        self.camera_info_msg.header.frame_id = self.frame_id
        self.camera_info_pub.publish(self.camera_info_msg)


def main(args=None):
    rclpy.init(args=args)

    node = FakeMonoCameraNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
