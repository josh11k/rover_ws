"""grid_node + identify_obstacles_node combined.

Consumes the fused global point cloud (lidar + stereo, already in
base_link) and publishes an OccupancyGrid traversability map, reusing the
elevation-grid / traversability algorithm from terrain_analysis.py (ported
from rover_lidar/lidar_processing_node.py).

Diagram nodes covered: grid_node ("convert points into blocks") and
identify_obstacles_node ("finds local height differences, which could mean
obstacle").
"""

import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Pose

import sensor_msgs_py.point_cloud2 as pc2

from rover_perception.terrain_analysis import (
    build_elevation_grid,
    compute_traversability,
)


DEFAULTS = {
    "points_topic": "/perception/global_points",
    "traversability_topic": "/terrain/traversability_grid",
    "output_frame_id": "base_link",

    "grid_resolution": 0.25,
    "grid_size_x": 100.0,
    "grid_size_y": 100.0,

    "max_step_height": 0.20,
    "max_roughness": 0.10,
    "max_slope_deg": 18.0,
    "min_points_per_cell": 2,
    "min_points_for_plane_fit": 4,
}


class ObstacleGridNode(Node):

    def __init__(self):
        super().__init__("obstacle_grid_node")

        self._declare_parameters()
        self._load_parameters()

        self.grid_width = int(self.grid_size_x / self.grid_resolution)
        self.grid_height = int(self.grid_size_y / self.grid_resolution)

        self.sub = self.create_subscription(
            PointCloud2,
            self.points_topic,
            self.cloud_callback,
            10,
        )

        self.pub = self.create_publisher(
            OccupancyGrid,
            self.traversability_topic,
            10,
        )

        self.get_logger().info(
            f"obstacle_grid_node: {self.points_topic} -> "
            f"{self.traversability_topic} "
            f"({self.grid_width}x{self.grid_height} cells @ "
            f"{self.grid_resolution} m)"
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

            elevation = build_elevation_grid(
                points,
                self.grid_resolution,
                self.grid_size_x,
                self.grid_size_y,
                self.grid_width,
                self.grid_height,
                self.min_points_for_plane_fit,
            )

            traversability = compute_traversability(
                elevation,
                self.grid_width,
                self.grid_height,
                self.grid_resolution,
                self.max_step_height,
                self.max_roughness,
                self.max_slope_deg,
                self.min_points_per_cell,
            )

            self.publish_occupancy_grid(
                traversability, msg.header.stamp,
                self.output_frame_id or msg.header.frame_id or "base_link",
            )

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"cloud_callback failed: {exc}")

    def publish_occupancy_grid(self, traversability: np.ndarray, stamp, frame_id: str):
        msg = OccupancyGrid()

        msg.header.stamp = stamp
        msg.header.frame_id = frame_id

        msg.info.resolution = self.grid_resolution
        msg.info.width = self.grid_width
        msg.info.height = self.grid_height

        msg.info.origin = Pose()
        msg.info.origin.position.x = -self.grid_size_x / 2.0
        msg.info.origin.position.y = -self.grid_size_y / 2.0
        msg.info.origin.position.z = 0.0
        msg.info.origin.orientation.w = 1.0

        msg.data = traversability.flatten().tolist()

        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = ObstacleGridNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
