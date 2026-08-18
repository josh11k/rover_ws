"""Generic PointCloud2 preprocessing node (diagram's "preprocessing_node").

Applies crop / voxel-downsample / radius-outlier-removal (in that order,
each individually toggleable) using the shared primitives in
pointcloud_filters.py. Instantiate once per sensor branch (lidar, stereo)
via launch args with different topics/params -- noise characteristics
differ enough between a LiDAR and a stereo depth sensor that the filter
*parameters* should stay per-sensor even though the filter *code* is
shared.

Points are carried through this node as (N, 4): x, y, z, weight (see
pointcloud_filters.py). Not every source has a weight yet -- the stereo
branch (stereo_pointcloud_node) computes a real one, the raw Livox topic
does not. If the incoming cloud has no "weight" field, one is synthesized
here with a constant 1.0 (full confidence), so every node downstream of
this one can assume 4 columns unconditionally, regardless of which sensor
branch it came from.
"""

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2
from rover_control_msgs.msg import OperationalModeSettings

from rover_perception.pointcloud_filters import (
    crop_filter,
    voxel_grid_filter,
    radius_outlier_filter,
    create_weighted_cloud,
    read_weighted_points,
)


DEFAULTS = {
    "input_topic": "/lidar/points_mast_base_link",
    "output_topic": "/lidar/points_filtered",
    "state_topic": "/operational_mode/settings",
    # Which field of OperationalModeSettings this instance follows -- see
    # frame_transform_node.py's DEFAULTS for the full explanation. Empty by
    # default (fails closed); MUST be set per instance in the launch file
    # ("lidar" for the lidar branch, "stereo_cam" for the stereo branch).
    "state_field": "",

    "enable_crop": True,
    "min_x": -50.0, "max_x": 50.0,
    "min_y": -50.0, "max_y": 50.0,
    "min_z": -10.0, "max_z": 10.0,

    "enable_voxel": True,
    "voxel_size": 0.10,

    "enable_outlier_removal": True,
    "outlier_radius": 0.30,
    "min_neighbors": 2,
}


class PointcloudPreprocessingNode(Node):

    def __init__(self):
        super().__init__("pointcloud_preprocessing_node")

        self._declare_parameters()
        self._load_parameters()
        self.state = "OFF"

        self.sub = None
        self.pub = None
        
        self.state_sub = self.create_subscription(
            OperationalModeSettings,
            self.state_topic,
            self.state_callback,
            10,
        )

    def state_callback(self, msg):
        if not self.state_field:
            self.get_logger().error(
                "state_field parameter is not set -- this "
                "pointcloud_preprocessing_node instance doesn't know which "
                "OperationalModeSettings field to follow (lidar / stereo_cam "
                "/ mono_cam / make_global_pointcloud). Staying OFF. Set "
                "'state_field' explicitly in the launch file for this node "
                "instance.",
                throttle_duration_sec=10.0,
            )
            return

        self.state = getattr(msg, self.state_field, "OFF")

        if self.state == "OFF":
            self.get_logger().info(f"pointcloud_preprocessing_node: OFF")

            if self.sub is not None:
                self.destroy_subscription(self.sub)
                self.sub = None
            if self.pub is not None:
                self.destroy_publisher(self.pub)
                self.pub = None

        elif self.state == "ON":
            self.get_logger().info(f"pointcloud_preprocessing_node: ON")

            self.sub = self.create_subscription(
                PointCloud2,
                self.input_topic,
                self.cloud_callback,
                qos_profile_sensor_data,
            )

            self.pub = self.create_publisher(
                PointCloud2,
                self.output_topic,
                10,
            )

            self.get_logger().info(
                f"pointcloud_preprocessing_node: {self.input_topic} -> "
                f"{self.output_topic} "
                f"(crop={self.enable_crop}, voxel={self.enable_voxel}, "
                f"outlier={self.enable_outlier_removal})"
            )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def _read_points_with_weight(self, msg: PointCloud2) -> np.ndarray:
        field_names = {f.name for f in msg.fields}

        if "weight" in field_names:
            return read_weighted_points(msg)

        # Deliberately not read_points_numpy(): it asserts that every
        # requested field shares the exact same datatype as the message's
        # *first* field overall (not just among x/y/z) -- see its own
        # error message "All fields need to have the same datatype. Use
        # `read_points()` otherwise." That assumption breaks on real
        # sensor drivers whose PointCloud2 field order/dtypes don't
        # happen to put x first (e.g. Livox clouds, which interleave
        # intensity/tag/line/timestamp fields of other dtypes). read_points()
        # has no such restriction -- it returns each field in its own
        # native dtype via a structured array, which we then cast down
        # ourselves.
        structured = pc2.read_points(
            msg, field_names=("x", "y", "z"), skip_nans=True
        )
        xyz = np.column_stack(
            [structured["x"], structured["y"], structured["z"]]
        ).astype(np.float32)

        weight = np.ones((len(xyz), 1), dtype=np.float32)
        return np.concatenate([xyz, weight], axis=1)

    def cloud_callback(self, msg: PointCloud2):
        try:
            points = self._read_points_with_weight(msg)

            if points.size == 0:
                return

            if self.enable_crop:
                points = crop_filter(
                    points,
                    self.min_x, self.max_x,
                    self.min_y, self.max_y,
                    self.min_z, self.max_z,
                )

            if self.enable_voxel and len(points) > 0:
                points = voxel_grid_filter(points, self.voxel_size)

            if self.enable_outlier_removal and len(points) > 0:
                points = radius_outlier_filter(
                    points, self.outlier_radius, self.min_neighbors
                )

            if len(points) == 0:
                return

            out_msg = create_weighted_cloud(msg.header, points)
            self.pub.publish(out_msg)

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"cloud_callback failed: {exc}")


def main(args=None):
    rclpy.init(args=args)

    node = PointcloudPreprocessingNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
