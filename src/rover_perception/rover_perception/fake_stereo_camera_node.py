"""Hardware-agnostic fake stereo-camera (depth) node.

This mirrors the diagram's "stereo_camera_node" (acquires data from stereo
cam) using the same fake-hardware convention already used elsewhere in this
workspace (see rover_control/fake_stm32_bridge_node.py's FakeUsbInterface and
rover_lidar/fake_lidar_node.py).

Topic names and message layout intentionally match what the official
Intel RealSense ROS2 wrapper (realsense2_camera) publishes for a D400-series
depth stream:

    /camera/depth/image_rect_raw   sensor_msgs/Image, encoding "16UC1", depth
                                    in millimeters, 0 = invalid pixel
    /camera/depth/camera_info      sensor_msgs/CameraInfo, rectified
                                    intrinsics (no distortion, matches
                                    "_rect_" data)

Frame: camera_depth_optical_frame, using the REP-103 optical convention
(Z forward / X right / Y down) that realsense2_camera also uses. Downstream
nodes (stereo_pointcloud_node, frame_transform_node) are written against
this convention, so once real hardware is available the swap is:
remove this node from the launch file and launch realsense2_camera instead
-- no other node needs to change.

The synthetic scene is a flat floor plane plus a single box-shaped
"obstacle" so the rest of the pipeline (pointcloud conversion, fusion,
traversability grid) has something non-trivial to chew on while no real
camera is attached.

Also publishes /camera/imu (sensor_msgs/Imu) -- the D435i variant's built-in
IMU, matching what realsense2_camera itself publishes. Held level (identity
orientation, i.e. camera assumed mounted upright) since the fake camera
doesn't otherwise move; this feeds mast_pose_node's platform-IMU
cross-check (see that node for why).
"""

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image, CameraInfo, Imu


DEFAULTS = {
    "depth_topic": "/camera/depth/image_rect_raw",
    "camera_info_topic": "/camera/depth/camera_info",
    "imu_topic": "/camera/imu",
    "frame_id": "camera_depth_optical_frame",

    "width": 640,
    "height": 480,
    "fps": 30.0,

    # Synthetic pinhole intrinsics, roughly matching a D435 640x480 depth
    # stream. Replace with the real calibrated values from camera_info once
    # actual hardware + Livox/RealSense calibration is available.
    "fx": 386.0,
    "fy": 386.0,
    "cx": 320.5,
    "cy": 240.5,

    # Camera mounted "camera_height_m" above the ground, looking
    # horizontally: used to synthesize a plausible floor-plane depth image.
    "camera_height_m": 0.5,
    "max_range_m": 8.0,

    # Fake box obstacle in front of the camera (meters, in camera optical
    # frame: x=right, y=down, z=forward).
    "obstacle_distance_m": 2.5,
    "obstacle_half_width_m": 0.4,
    "obstacle_half_height_m": 0.4,
}


class FakeStereoCameraInterface:
    """Stand-in for a real depth-camera SDK (e.g. pyrealsense2).

    Generates a synthetic 16-bit depth frame (millimeters) each call to
    get_depth_frame(). Swapping to real hardware later means replacing only
    this class (and ideally just launching the vendor's ROS2 driver
    instead of this whole node).
    """

    def __init__(self, width, height, fx, fy, cx, cy, camera_height_m,
                 max_range_m, obstacle_distance_m, obstacle_half_width_m,
                 obstacle_half_height_m):
        self.width = width
        self.height = height
        self.fx = fx
        self.fy = fy
        self.cx = cx
        self.cy = cy
        self.camera_height_m = camera_height_m
        self.max_range_m = max_range_m
        self.obstacle_distance_m = obstacle_distance_m
        self.obstacle_half_width_m = obstacle_half_width_m
        self.obstacle_half_height_m = obstacle_half_height_m

        # Precompute per-pixel viewing rays (vectorized, done once).
        us, vs = np.meshgrid(
            np.arange(width, dtype=np.float32),
            np.arange(height, dtype=np.float32),
        )
        self._ray_x = (us - cx) / fx
        self._ray_y = (vs - cy) / fy

    def get_depth_frame_mm(self) -> np.ndarray:
        """Return a (height, width) uint16 depth image in millimeters."""

        # Floor plane: camera looks along +Z (optical frame), floor is
        # camera_height_m below the optical center, i.e. Y = camera_height_m
        # in the optical frame. For a ray (ray_x, ray_y, 1)*z, solving
        # ray_y * z == camera_height_m gives the floor depth per pixel.
        with np.errstate(divide="ignore", invalid="ignore"):
            floor_z = np.where(
                self._ray_y > 1e-6,
                self.camera_height_m / self._ray_y,
                np.inf,
            )

        depth_m = np.clip(floor_z, 0.0, self.max_range_m)

        # Rectangular box obstacle at a fixed distance, centered in FOV.
        box_z = self.obstacle_distance_m
        world_x = self._ray_x * box_z
        world_y = self._ray_y * box_z

        in_box = (
            (np.abs(world_x) <= self.obstacle_half_width_m)
            & (world_y <= self.obstacle_half_height_m)
            & (world_y >= -self.obstacle_half_height_m)
        )
        depth_m = np.where(in_box & (box_z < depth_m), box_z, depth_m)

        # Invalid pixels (looking above horizon, or beyond max range).
        invalid = ~np.isfinite(depth_m) | (depth_m >= self.max_range_m)
        depth_mm = (depth_m * 1000.0).astype(np.uint16)
        depth_mm[invalid] = 0

        return depth_mm


class FakeStereoCameraNode(Node):

    def __init__(self):
        super().__init__("fake_stereo_camera_node")

        self._declare_parameters()
        self._load_parameters()

        self.interface = FakeStereoCameraInterface(
            width=self.width,
            height=self.height,
            fx=self.fx,
            fy=self.fy,
            cx=self.cx,
            cy=self.cy,
            camera_height_m=self.camera_height_m,
            max_range_m=self.max_range_m,
            obstacle_distance_m=self.obstacle_distance_m,
            obstacle_half_width_m=self.obstacle_half_width_m,
            obstacle_half_height_m=self.obstacle_half_height_m,
        )

        self.depth_pub = self.create_publisher(
            Image,
            self.depth_topic,
            qos_profile_sensor_data,
        )

        self.camera_info_pub = self.create_publisher(
            CameraInfo,
            self.camera_info_topic,
            qos_profile_sensor_data,
        )

        self.imu_pub = self.create_publisher(
            Imu,
            self.imu_topic,
            qos_profile_sensor_data,
        )

        self.camera_info_msg = self._build_camera_info()

        period = 1.0 / self.fps
        self.timer = self.create_timer(period, self.timer_callback)

        self.get_logger().info(
            f"Fake stereo camera started: {self.width}x{self.height} "
            f"@ {self.fps} FPS, publishing to {self.depth_topic}"
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
        depth_mm = self.interface.get_depth_frame_mm()
        stamp = self.get_clock().now().to_msg()

        depth_msg = Image()
        depth_msg.header.stamp = stamp
        depth_msg.header.frame_id = self.frame_id
        depth_msg.height = self.height
        depth_msg.width = self.width
        depth_msg.encoding = "16UC1"
        depth_msg.is_bigendian = 0
        depth_msg.step = self.width * 2
        depth_msg.data = depth_mm.tobytes()
        self.depth_pub.publish(depth_msg)

        self.camera_info_msg.header.stamp = stamp
        self.camera_info_msg.header.frame_id = self.frame_id
        self.camera_info_pub.publish(self.camera_info_msg)

        imu_msg = Imu()
        imu_msg.header.stamp = stamp
        imu_msg.header.frame_id = self.frame_id
        # Identity orientation (camera held level) -- valid, per
        # sensor_msgs/Imu convention (orientation_covariance[0] != -1 means
        # "orientation is provided").
        imu_msg.orientation.w = 1.0
        imu_msg.orientation_covariance = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
        imu_msg.linear_acceleration.z = 9.81
        self.imu_pub.publish(imu_msg)


def main(args=None):
    rclpy.init(args=args)

    node = FakeStereoCameraNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
