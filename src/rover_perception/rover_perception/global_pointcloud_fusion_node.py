"""Merge the (already transformed + filtered) lidar and stereo clouds.

This is the diagram's "make_global_pointcloud_node" ("combine stereocam and
lidar point cloud into one"). By the time clouds reach this node they have
already been:

  1. transformed into base_link by frame_transform_node, and
  2. cropped / downsampled / outlier-filtered by pointcloud_preprocessing_node
     (which also guarantees both clouds carry a 4th "weight" field by now,
     see pointcloud_filters.py)

so this node's job is just a time-synchronized concatenation, not another
round of sensor-specific processing. The per-point weight is passed through
unchanged -- it's consumed downstream by terrain_analysis.py.
"""

import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import PointCloud2

import message_filters

from rover_perception.pointcloud_filters import (
    create_weighted_cloud,
    read_weighted_points,
)


DEFAULTS = {
    "lidar_points_topic": "/lidar/points_filtered",
    "stereo_points_topic": "/stereo/points_filtered",
    "output_topic": "/perception/global_points",
    "output_frame_id": "base_link",
    "sync_slop_sec": 0.10,
}


class GlobalPointcloudFusionNode(Node):

    def __init__(self):
        super().__init__("global_pointcloud_fusion_node")

        self._declare_parameters()
        self._load_parameters()

        self.pub = self.create_publisher(
            PointCloud2,
            self.output_topic,
            10,
        )

        self.lidar_sub = message_filters.Subscriber(
            self, PointCloud2, self.lidar_points_topic
        )
        self.stereo_sub = message_filters.Subscriber(
            self, PointCloud2, self.stereo_points_topic
        )

        self.sync = message_filters.ApproximateTimeSynchronizer(
            [self.lidar_sub, self.stereo_sub],
            queue_size=10,
            slop=self.sync_slop_sec,
        )
        self.sync.registerCallback(self.fusion_callback)

        self.get_logger().info(
            f"global_pointcloud_fusion_node: {self.lidar_points_topic} + "
            f"{self.stereo_points_topic} -> {self.output_topic}"
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def fusion_callback(self, lidar_msg: PointCloud2, stereo_msg: PointCloud2):
        try:
            lidar_points = read_weighted_points(lidar_msg)
            stereo_points = read_weighted_points(stereo_msg)

            if lidar_points.size == 0 and stereo_points.size == 0:
                return

            if lidar_points.size == 0:
                combined = stereo_points
            elif stereo_points.size == 0:
                combined = lidar_points
            else:
                combined = np.concatenate(
                    [lidar_points, stereo_points], axis=0
                )

            # Use the later of the two stamps so downstream consumers see a
            # timestamp that's never older than either source cloud.
            lidar_stamp = (
                lidar_msg.header.stamp.sec
                + lidar_msg.header.stamp.nanosec * 1e-9
            )
            stereo_stamp = (
                stereo_msg.header.stamp.sec
                + stereo_msg.header.stamp.nanosec * 1e-9
            )
            newest_header = (
                lidar_msg.header
                if lidar_stamp >= stereo_stamp
                else stereo_msg.header
            )

            newest_header.frame_id = self.output_frame_id
            out_msg = create_weighted_cloud(newest_header, combined)
            self.pub.publish(out_msg)

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"fusion_callback failed: {exc}")


def main(args=None):
    rclpy.init(args=args)

    node = GlobalPointcloudFusionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
