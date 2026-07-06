"""Depth image + intrinsics -> PointCloud2.

This is the diagram's "make_point_cloud_node" ("convert distance to z-axis
value"): it turns the stereo camera's rectified depth image into a 3D point
cloud in the camera's optical frame, using vectorized numpy pinhole
back-projection (same style as rover_lidar/lidar_processing_node.py's
vectorized filters).

Each point also gets a 4th "weight" field (0..1) expressing how much it
should be trusted downstream. Stereo depth is known to degrade with
distance (triangulation error grows roughly with z^2) and in low light, so:

    weight = distance_weight(z) * scene_confidence

- distance_weight(z) = 1 / (1 + (z / distance_weight_ref_m)^2), hard-zeroed
  beyond max_reliable_range_m.
- scene_confidence is a global (0..1) scalar received on
  scene_confidence_topic, meant to be published by a future brightness /
  low-light-detection node. No such node exists yet, so it simply defaults
  to 1.0 (no light-based penalty) until something publishes to that topic --
  the wiring is real and testable today (e.g. `ros2 topic pub` a low value
  to see the weighting/traversability react), only the upstream signal is
  still a TODO.

The diagram's "tbd / optional" stage between stereo_camera_node and this
node is left as an explicit gap for now (e.g. temporal filtering / hole
filling on the raw depth image) -- there's nothing to design against yet, so
this node currently subscribes directly to the depth image. Insert an extra
node in the launch file later if that stage gets defined.
"""

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image, CameraInfo, PointCloud2
from std_msgs.msg import Float32

import message_filters

from rover_perception.pointcloud_filters import create_weighted_cloud


DEFAULTS = {
    "depth_topic": "/camera/depth/image_rect_raw",
    "camera_info_topic": "/camera/depth/camera_info",
    "points_topic": "/stereo/points",

    # Skip every Nth pixel in each axis to bound point count / CPU load.
    # 1 = full resolution.
    "pixel_stride": 2,

    # Depth values (in the 16UC1 image, millimeters) outside this range are
    # dropped as invalid, mirroring typical stereo-depth min/max Z limits.
    "min_depth_m": 0.2,
    "max_depth_m": 10.0,

    "sync_slop_sec": 0.05,

    # Per-point weight (0..1): how much to trust this point downstream.
    # distance_weight = 1 / (1 + (z / distance_weight_ref_m)^2), i.e. ~0.5
    # at distance_weight_ref_m and falling off from there; hard-zeroed
    # beyond max_reliable_range_m regardless of what the formula gives.
    "distance_weight_ref_m": 2.5,
    "max_reliable_range_m": 6.0,

    # Global (0..1) light/scene-confidence multiplier, received from an
    # external node. Not implemented yet -- defaults to 1.0 (no penalty)
    # until something publishes here.
    "scene_confidence_topic": "/camera/scene_confidence",
}


class StereoPointcloudNode(Node):

    def __init__(self):
        super().__init__("stereo_pointcloud_node")

        self._declare_parameters()
        self._load_parameters()

        self._scene_confidence = 1.0

        self.points_pub = self.create_publisher(
            PointCloud2,
            self.points_topic,
            10,
        )

        self.depth_sub = message_filters.Subscriber(
            self, Image, self.depth_topic, qos_profile=qos_profile_sensor_data
        )
        self.info_sub = message_filters.Subscriber(
            self, CameraInfo, self.camera_info_topic,
            qos_profile=qos_profile_sensor_data
        )

        self.sync = message_filters.ApproximateTimeSynchronizer(
            [self.depth_sub, self.info_sub],
            queue_size=10,
            slop=self.sync_slop_sec,
        )
        self.sync.registerCallback(self.depth_callback)

        self.scene_confidence_sub = self.create_subscription(
            Float32,
            self.scene_confidence_topic,
            self._scene_confidence_callback,
            10,
        )

        # Cached per-(width,height) ray directions, rebuilt if intrinsics
        # or resolution change.
        self._cached_shape = None
        self._ray_x = None
        self._ray_y = None

        self.get_logger().info(
            f"stereo_pointcloud_node: {self.depth_topic} + "
            f"{self.camera_info_topic} -> {self.points_topic} "
            f"(weight = distance x scene_confidence, scene_confidence from "
            f"{self.scene_confidence_topic}, default 1.0)"
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def _scene_confidence_callback(self, msg: Float32):
        self._scene_confidence = float(np.clip(msg.data, 0.0, 1.0))

    def _update_ray_cache(self, width, height, fx, fy, cx, cy):
        stride = max(1, self.pixel_stride)
        shape_key = (width, height, stride, fx, fy, cx, cy)

        if self._cached_shape == shape_key:
            return

        us = np.arange(0, width, stride, dtype=np.float32)
        vs = np.arange(0, height, stride, dtype=np.float32)
        grid_u, grid_v = np.meshgrid(us, vs)

        self._ray_x = (grid_u - cx) / fx
        self._ray_y = (grid_v - cy) / fy
        self._stride = stride
        self._cached_shape = shape_key

    def depth_callback(self, depth_msg: Image, info_msg: CameraInfo):
        try:
            if depth_msg.encoding != "16UC1":
                self.get_logger().warn(
                    f"Unexpected depth encoding '{depth_msg.encoding}', "
                    "expected 16UC1. Skipping frame.",
                    throttle_duration_sec=5.0,
                )
                return

            depth_mm = np.frombuffer(
                depth_msg.data, dtype=np.uint16
            ).reshape(depth_msg.height, depth_msg.width)

            fx, fy = info_msg.k[0], info_msg.k[4]
            cx, cy = info_msg.k[2], info_msg.k[5]

            self._update_ray_cache(
                depth_msg.width, depth_msg.height, fx, fy, cx, cy
            )

            depth_m = (
                depth_mm[::self._stride, ::self._stride].astype(np.float32)
                / 1000.0
            )

            valid = (
                (depth_m >= self.min_depth_m)
                & (depth_m <= self.max_depth_m)
            )

            z = depth_m[valid]
            x = self._ray_x[valid] * z
            y = self._ray_y[valid] * z

            if z.size == 0:
                return

            distance_weight = 1.0 / (
                1.0 + (z / self.distance_weight_ref_m) ** 2
            )
            distance_weight = np.where(
                z > self.max_reliable_range_m, 0.0, distance_weight
            )
            weight = np.clip(
                distance_weight * self._scene_confidence, 0.0, 1.0
            )

            points = np.stack([x, y, z, weight], axis=-1).astype(np.float32)

            cloud_msg = create_weighted_cloud(depth_msg.header, points)
            self.points_pub.publish(cloud_msg)

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"depth_callback failed: {exc}")


def main(args=None):
    rclpy.init(args=args)

    node = StereoPointcloudNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
