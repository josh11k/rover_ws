"""Generic PointCloud2 preprocessing node (diagram's "preprocessing_node").

Applies crop / voxel-downsample / radius-outlier-removal (in that order,
each individually toggleable) using the shared primitives in
pointcloud_filters.py. Instantiate once per sensor branch (lidar, stereo)
via launch args with different topics/params -- noise characteristics
differ enough between a LiDAR and a stereo depth sensor that the filter
*parameters* should stay per-sensor even though the filter *code* is
shared.
"""

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import PointCloud2
import sensor_msgs_py.point_cloud2 as pc2

from rover_perception.pointcloud_filters import (
    crop_filter,
    voxel_grid_filter,
    radius_outlier_filter,
)


DEFAULTS = {
    "input_topic": "/lidar/points_base_link",
    "output_topic": "/lidar/points_filtered",

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

    def cloud_callback(self, msg: PointCloud2):
        try:
            points = pc2.read_points_numpy(
                msg, field_names=("x", "y", "z"), skip_nans=True
            ).astype(np.float32)

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

            out_msg = pc2.create_cloud_xyz32(msg.header, points)
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
