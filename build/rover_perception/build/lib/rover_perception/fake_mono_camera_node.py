"""Hardware-agnostic fake mono-camera node.

This is the diagram's "mono_cam_node" ("acquires data from mono cam"), the
entry point of the LED-detection branch (mono_cam_node -> led_detector_node
-> position_rover_node). Same fake-hardware convention as elsewhere in this
workspace (FakeUsbInterface, FakeStereoCameraInterface): a small interface
class stands in for the real camera SDK, swappable later without touching
the ROS2 node around it.

Setup (see ARCHITECTURE.md): this mono-cam is mounted on the same fixed
mast as the rest of the perception module and observes a single, separate
rover driving around it. The rover carries a known, rigid LED pattern: 5
LEDs arranged like the "5" face of a die (4 corners of a square + 1 center),
same color (green -- matches led_detector_node's color filter), known
spacing. led_detector_node finds individual blobs;
matching the detected blobs against this known pattern to solve for the
rover's distance/position (a PnP-style problem, like optical motion-capture
markers) is position_rover_node's job, not this node's or led_detector's.

So the fake scene here simulates one rigid rover pattern moving through the
frame -- not several independent blobs -- with:
  - distance from the mast oscillating (rover driving closer/further),
  - lateral position oscillating on a different period (driving side to
    side / around the mast), and
  - the whole pattern slowly rotating (yaw), so the projected square
    foreshortens as if the rover were turning -- giving a future
    position_rover_node varying orientations to solve for, not just
    varying positions.
Each LED's apparent pixel size and brightness-blob radius shrinks with
distance (1/Z), matching real perspective.

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
right, Y down) -- same convention used for the stereo camera. Not yet wired
into the launch file's static-TF chain (mast_link -> mono_cam_optical_frame)
-- that's the next step after this node.
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

    # The rover's known LED pattern: "5" on a die -- 4 corners of a square
    # (edge length = 2 * pattern_half_size_m) + 1 center LED, all the same
    # color. Placeholder geometry until the real pattern is finalized.
    # Color: LEDs are expected to be green (matches led_detector_node's
    # min_green_dominance color filter).
    "pattern_half_size_m": 0.15,
    "led_color_r": 60,
    "led_color_g": 255,
    "led_color_b": 80,

    # Apparent blob radius (pixels) at 1m distance; actual radius scales
    # as 1/distance (perspective), clamped to this range.
    "led_apparent_radius_px_at_1m": 20.0,
    "min_led_radius_px": 2.0,
    "max_led_radius_px": 40.0,

    # Rover motion, simulated directly in the camera's optical frame
    # (no mast_link roundtrip needed for a synthetic scene): distance and
    # lateral position each oscillate on their own period (different
    # periods -> a more organic, non-repeating path), plus a slow yaw
    # rotation of the whole pattern.
    "rover_center_distance_m": 3.0,
    "rover_distance_amplitude_m": 1.5,
    "rover_distance_period_s": 20.0,
    "rover_lateral_amplitude_m": 2.0,
    "rover_lateral_period_s": 14.0,
    "rover_height_m": 0.3,
    "rover_yaw_period_s": 11.0,

    "background_noise_std": 5.0,
}


class FakeMonoCameraInterface:
    """Stand-in for a real camera SDK / v4l2 capture loop.

    Generates a synthetic RGB8 frame each call to get_frame(t): a noisy dark
    background plus the rover's 5-LED "die" pattern, projected via a pinhole
    model as the pattern moves and rotates over time. Swapping to real
    hardware later means replacing only this class (and ideally just
    launching v4l2_camera instead of this whole node).
    """

    def __init__(
        self, width, height, fx, fy, cx, cy,
        pattern_half_size_m, led_color,
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
        self.led_color = led_color

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

        # The "5" pattern: 4 square corners + 1 center, in the pattern's own
        # local plane (local z=0, flat panel). Rotated by the pattern's yaw
        # and placed at the rover's current position each frame.
        s = pattern_half_size_m
        self._local_led_positions = np.array([
            (-s, -s, 0.0),
            (s, -s, 0.0),
            (-s, s, 0.0),
            (s, s, 0.0),
            (0.0, 0.0, 0.0),
        ], dtype=np.float64)

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

        theta = yaw_omega * t
        cos_t, sin_t = math.cos(theta), math.sin(theta)

        for xl, yl, zl in self._local_led_positions:
            # Yaw rotation about the vertical (Y) axis: mixes local x/z,
            # leaves y (height) unchanged -- simulates the rover turning.
            x_rot = xl * cos_t - zl * sin_t
            z_rot = xl * sin_t + zl * cos_t

            x = center_x + x_rot
            y = center_y + yl
            z = center_z + z_rot

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
            frame[mask] = self.led_color

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
            pattern_half_size_m=self.pattern_half_size_m,
            led_color=(self.led_color_r, self.led_color_g, self.led_color_b),
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
            f"@ {self.fps} FPS, simulating a 5-LED die pattern at "
            f"~{self.rover_center_distance_m}m, publishing to "
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
