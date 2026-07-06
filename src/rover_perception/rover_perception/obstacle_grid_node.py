"""grid_node + identify_obstacles_node combined.

Consumes the fused global point cloud (lidar + stereo, already in
mast_base_link -- the mast's own quasi-static frame, only moves under real
mast lean, not with pan/tilt) and publishes an OccupancyGrid traversability
map, reusing the
elevation-grid / traversability algorithm from terrain_analysis.py (ported
from rover_lidar/lidar_processing_node.py).

Diagram nodes covered: grid_node ("convert points into blocks") and
identify_obstacles_node ("finds local height differences, which could mean
obstacle").

Persistent per-cell point buffer
---------------------------------
`global_pointcloud_fusion_node` only ever hands us a single *instant* --
lidar+stereo synchronized to one moment in time. On real hardware (spinning
lidar, panning mast) each instant only covers whatever the sensors happened
to see right then; without memory the grid would forget everything from
previous instants and never build up a full picture across a pan sweep.

To fix that, this node keeps a persistent point buffer *per grid cell*
(`self.cell_buffers`), independent of `terrain_analysis.py` (which stays a
pure, stateless function of "whatever points you hand it"). Every incoming
cloud's points are sorted into their cell's buffer; each buffer is a
`collections.deque(maxlen=max_points_per_cell)`, so once a cell is full the
oldest point is dropped automatically as a new one arrives -- a
continuously sliding/rolling window, not a hard periodic reset. Each
callback then re-runs `build_elevation_grid()` over the *entire* buffered
point set (all cells combined), not just the newest message, so the
published grid reflects everything accumulated so far, gradually aged out
cell-by-cell rather than in discrete batches.
"""

from collections import deque

import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid, MapMetaData
from geometry_msgs.msg import Pose

from rover_perception_msgs.msg import TerrainGrid

from rover_perception.pointcloud_filters import read_weighted_points
from rover_perception.terrain_analysis import (
    build_elevation_grid,
    compute_traversability,
    flatten_elevation_grid,
)


DEFAULTS = {
    "points_topic": "/perception/global_points",
    "traversability_topic": "/terrain/traversability_grid",
    "terrain_stats_topic": "/terrain/terrain_grid_stats",
    "output_frame_id": "mast_base_link",

    "grid_resolution": 0.25,
    "grid_size_x": 100.0,
    "grid_size_y": 100.0,

    "max_step_height": 0.20,
    "max_roughness": 0.10,
    "max_slope_deg": 18.0,
    "min_points_per_cell": 2,
    "min_points_for_plane_fit": 4,

    # Persistent per-cell point buffer (rolling window across callbacks --
    # see module docstring). Each cell keeps at most this many of its most
    # recent points; the oldest is dropped first once the cap is reached.
    # Keep this modest: memory scales with (occupied cells) x this value,
    # and a few dozen points per cell is already plenty for a stable mean/
    # plane fit.
    "max_points_per_cell": 50,
}


class ObstacleGridNode(Node):

    def __init__(self):
        super().__init__("obstacle_grid_node")

        self._declare_parameters()
        self._load_parameters()

        self.grid_width = int(self.grid_size_x / self.grid_resolution)
        self.grid_height = int(self.grid_size_y / self.grid_resolution)

        # Persistent per-cell point buffers: (ix, iy) -> deque of (x,y,z,weight)
        # rows, capped at max_points_per_cell (oldest dropped first). This is
        # what makes the published grid accumulate across callbacks instead
        # of only reflecting the newest incoming cloud -- see module docstring.
        self.cell_buffers: dict = {}

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

        self.stats_pub = self.create_publisher(
            TerrainGrid,
            self.terrain_stats_topic,
            10,
        )

        self.get_logger().info(
            f"obstacle_grid_node: {self.points_topic} -> "
            f"{self.traversability_topic} + {self.terrain_stats_topic} "
            f"({self.grid_width}x{self.grid_height} cells @ "
            f"{self.grid_resolution} m, max {self.max_points_per_cell} "
            f"buffered points/cell)"
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def cloud_callback(self, msg: PointCloud2):
        try:
            new_points = read_weighted_points(msg)

            if new_points.size > 0:
                self._update_cell_buffers(new_points)

            if not self.cell_buffers:
                return

            points = self._collect_buffered_points()

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

            frame_id = (
                self.output_frame_id or msg.header.frame_id or "mast_base_link"
            )
            info = self._build_map_info()

            self.publish_occupancy_grid(
                traversability, msg.header.stamp, frame_id, info,
            )

            stats = flatten_elevation_grid(
                elevation, self.grid_width, self.grid_height,
            )
            self.publish_terrain_stats(
                traversability, stats, msg.header.stamp, frame_id, info,
            )

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"cloud_callback failed: {exc}")

    def _update_cell_buffers(self, points: np.ndarray):
        """Sort incoming points into their grid cell's rolling buffer.

        Uses the exact same cell-indexing convention as
        `terrain_analysis.build_elevation_grid()` (same origin/resolution),
        so a point ends up in the same cell here as it would if scored
        directly -- this is purely about *which points survive* into that
        later call, not a second/competing grid definition.
        """
        ix = np.floor(
            (points[:, 0] + self.grid_size_x / 2.0) / self.grid_resolution
        ).astype(np.int64)
        iy = np.floor(
            (points[:, 1] + self.grid_size_y / 2.0) / self.grid_resolution
        ).astype(np.int64)

        valid = (
            (ix >= 0) & (ix < self.grid_width)
            & (iy >= 0) & (iy < self.grid_height)
        )
        ix, iy, pts = ix[valid], iy[valid], points[valid]

        for i in range(len(pts)):
            key = (int(ix[i]), int(iy[i]))
            buf = self.cell_buffers.get(key)
            if buf is None:
                buf = deque(maxlen=self.max_points_per_cell)
                self.cell_buffers[key] = buf
            buf.append(pts[i])

    def _collect_buffered_points(self) -> np.ndarray:
        """Flatten all per-cell buffers back into one (N, 4) array, the
        input shape `build_elevation_grid()` already expects -- so that
        function itself needs no changes, it just now sees accumulated
        history instead of a single message's points.
        """
        if not self.cell_buffers:
            return np.empty((0, 4), dtype=np.float32)

        arrays = [
            np.array(buf, dtype=np.float32)
            for buf in self.cell_buffers.values()
            if len(buf) > 0
        ]

        if not arrays:
            return np.empty((0, 4), dtype=np.float32)

        return np.concatenate(arrays, axis=0)

    def _build_map_info(self) -> MapMetaData:
        """Shared grid metadata for both published topics, so cells line up
        1:1 between /terrain/traversability_grid and /terrain/terrain_grid_stats.
        """
        info = MapMetaData()
        info.resolution = self.grid_resolution
        info.width = self.grid_width
        info.height = self.grid_height

        info.origin = Pose()
        info.origin.position.x = -self.grid_size_x / 2.0
        info.origin.position.y = -self.grid_size_y / 2.0
        info.origin.position.z = 0.0
        info.origin.orientation.w = 1.0

        return info

    def publish_occupancy_grid(
        self, traversability: np.ndarray, stamp, frame_id: str, info: MapMetaData,
    ):
        msg = OccupancyGrid()

        msg.header.stamp = stamp
        msg.header.frame_id = frame_id
        msg.info = info
        msg.data = traversability.flatten().tolist()

        self.pub.publish(msg)

    def publish_terrain_stats(
        self,
        traversability: np.ndarray,
        stats: dict,
        stamp,
        frame_id: str,
        info: MapMetaData,
    ):
        msg = TerrainGrid()

        msg.header.stamp = stamp
        msg.header.frame_id = frame_id
        msg.info = info

        msg.traversability = traversability.flatten().tolist()
        msg.min_z = stats["min_z"].tolist()
        msg.max_z = stats["max_z"].tolist()
        msg.mean_z = stats["mean_z"].tolist()
        msg.roughness = stats["roughness"].tolist()
        msg.plane_slope_deg = stats["plane_slope_deg"].tolist()
        msg.point_count = stats["point_count"].tolist()
        msg.total_weight = stats["total_weight"].tolist()

        self.stats_pub.publish(msg)


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
