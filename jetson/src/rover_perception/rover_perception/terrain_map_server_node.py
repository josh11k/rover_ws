"""Load a previously saved terrain map (.npz, written by obstacle_grid_node's
save_terrain_map service -- see that node's module docstring) and republish
it once, using transient-local QoS so late-joining subscribers (e.g. a
rover-positioning node started well after this one) still receive it. This
is the same durability idiom Nav2's map_server uses for static maps: the
publisher only ever calls publish() once per topic, but ROS2 caches that
last message at the middleware level and hands it to anyone who subscribes
afterward, at any point in the future.

Meant to run standalone, AFTER the live mapping pipeline
(ground_segmentation_node + obstacle_grid_node) has done its one-time
detailed pre-deployment scan and been switched OFF -- see chat for the
intended two-phase workflow (mast does one detailed scan, then perception
goes quiet and the rover is tracked via the mono-cam LED branch instead,
using this republished map for positioning context). Not started by
stereo_lidar_fusion.launch.py; run it by hand once the scan is saved:

    ros2 run rover_perception terrain_map_server_node \\
        --ros-args -p map_path:=/home/team/rover_maps/terrain_map.npz

Always publishes two topics, one-shot/transient-local:
  - /terrain/traversability_grid (OccupancyGrid) and
    /terrain/terrain_grid_stats (TerrainGrid) -- the exact same
    topics/types obstacle_grid_node publishes live, so anything already
    consuming the live pipeline's output (RViz2, position_rover_node,
    etc.) can point at either source interchangeably without caring which
    one is currently running.

Point clouds -- off by default (added 2026-09)
--------------------------------------------------
save_terrain_map also stores the raw ground_points/obstacle_points arrays
(see obstacle_grid_node's module docstring). At the scan sizes this project
targets (60x60m, fine tiles, generous max_points_per_cell -- see
ground_segmentation_node) those arrays can be large: potentially hundreds
of thousands to millions of points, meaning a single PointCloud2 message in
the tens-to-hundreds-of-MB range. Publishing that is a one-time cost here
(not continuous, unlike the live pipeline), but combined with
TRANSIENT_LOCAL durability -- which makes the middleware hang onto that one
big message and resend it in full to every future subscriber -- it can mean
a real startup hiccup, and risks bumping into a DDS implementation's
default message-size/fragmentation limits.

Since the rover-operation phase this node is meant to serve only actually
needs the finished traversability grid (the raw point clouds are for
possible later re-segmentation/re-gridding at different parameters -- see
chat), the point cloud topics are gated behind a parameter and OFF by
default:

    publish_point_clouds (default: false)

Set it to true (e.g. `-p publish_point_clouds:=true`) if you specifically
want /perception/ground_points and /perception/obstacle_points republished
too. If you just want the raw points for offline reprocessing, reading the
.npz directly with numpy (no ROS involved) avoids the message-size concern
entirely:

    import numpy as np
    data = np.load("/home/team/rover_maps/terrain_map.npz")
    ground = data["ground_points"]      # (N, 4): x, y, z, weight
    obstacle = data["obstacle_points"]  # (M, 4): x, y, z, weight

If the loaded .npz predates the ground_points/obstacle_points fields
(saved before the 2026-09 change that added them), those two clouds are
skipped with a warning logged even if publish_point_clouds is true -- the
grid/stats topics still publish normally either way.
"""

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header
from nav_msgs.msg import OccupancyGrid, MapMetaData
from geometry_msgs.msg import Pose

from rover_perception_msgs.msg import TerrainGrid
from rover_perception.pointcloud_filters import create_weighted_cloud


DEFAULTS = {
    "map_path": "/home/team/rover_maps/terrain_map.npz",
    "traversability_topic": "/terrain/traversability_grid",
    "terrain_stats_topic": "/terrain/terrain_grid_stats",
    # Same topic names ground_segmentation_node publishes live -- see
    # module docstring.
    "ground_points_topic": "/perception/ground_points",
    "obstacle_points_topic": "/perception/obstacle_points",
    # Off by default -- see module docstring "Point clouds -- off by
    # default" section for why (potentially very large one-shot messages).
    "publish_point_clouds": False,
}


class TerrainMapServerNode(Node):

    def __init__(self):
        super().__init__("terrain_map_server_node")

        self._declare_parameters()
        self._load_parameters()

        # depth=1 + TRANSIENT_LOCAL + RELIABLE: publish once, but any
        # subscriber that comes up later still gets that one message
        # delivered to it -- see module docstring.
        qos = QoSProfile(
            depth=1,
            durability=DurabilityPolicy.TRANSIENT_LOCAL,
            reliability=ReliabilityPolicy.RELIABLE,
        )

        self.pub = self.create_publisher(
            OccupancyGrid, self.traversability_topic, qos,
        )
        self.stats_pub = self.create_publisher(
            TerrainGrid, self.terrain_stats_topic, qos,
        )

        # Only created if actually needed -- see module docstring "Point
        # clouds -- off by default" section.
        self.ground_pub = None
        self.obstacle_pub = None
        if self.publish_point_clouds:
            self.ground_pub = self.create_publisher(
                PointCloud2, self.ground_points_topic, qos,
            )
            self.obstacle_pub = self.create_publisher(
                PointCloud2, self.obstacle_points_topic, qos,
            )

        self._load_and_publish()

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def _load_and_publish(self):
        try:
            data = np.load(self.map_path, allow_pickle=False)
        except Exception as exc:  # noqa: BLE001 - report, don't crash
            self.get_logger().error(
                f"terrain_map_server_node: failed to load {self.map_path}: {exc}"
            )
            return

        try:
            resolution = float(data["grid_resolution"])
            width = int(data["grid_width"])
            height = int(data["grid_height"])
            size_x = float(data["grid_size_x"])
            size_y = float(data["grid_size_y"])
            frame_id = str(data["frame_id"])

            info = MapMetaData()
            info.resolution = resolution
            info.width = width
            info.height = height
            info.origin = Pose()
            info.origin.position.x = -size_x / 2.0
            info.origin.position.y = -size_y / 2.0
            info.origin.position.z = 0.0
            info.origin.orientation.w = 1.0

            now = self.get_clock().now().to_msg()

            grid_msg = OccupancyGrid()
            grid_msg.header.stamp = now
            grid_msg.header.frame_id = frame_id
            grid_msg.info = info
            grid_msg.data = data["traversability"].flatten().tolist()
            self.pub.publish(grid_msg)

            stats_msg = TerrainGrid()
            stats_msg.header.stamp = now
            stats_msg.header.frame_id = frame_id
            stats_msg.info = info
            stats_msg.traversability = data["traversability"].flatten().tolist()
            stats_msg.min_z = data["min_z"].flatten().tolist()
            stats_msg.max_z = data["max_z"].flatten().tolist()
            stats_msg.mean_z = data["mean_z"].flatten().tolist()
            stats_msg.roughness = data["roughness"].flatten().tolist()
            stats_msg.plane_slope_deg = data["plane_slope_deg"].flatten().tolist()
            stats_msg.point_count = data["point_count"].flatten().tolist()
            stats_msg.total_weight = data["total_weight"].flatten().tolist()
            self.stats_pub.publish(stats_msg)

            summary = (
                f"terrain_map_server_node: loaded {self.map_path} "
                f"({width}x{height} cells @ {resolution} m, frame_id="
                f"'{frame_id}') -> {self.traversability_topic} + "
                f"{self.terrain_stats_topic} (transient-local, one-shot)"
            )

            # Point clouds: off by default -- see module docstring "Point
            # clouds -- off by default" section. Each stored array is
            # (N, 4) x/y/z/weight, same layout create_weighted_cloud()
            # expects.
            if self.publish_point_clouds:
                ground_count = self._publish_saved_cloud(
                    data, "ground_points", self.ground_pub, now, frame_id,
                )
                obstacle_count = self._publish_saved_cloud(
                    data, "obstacle_points", self.obstacle_pub, now, frame_id,
                )
                summary += (
                    f"; also {self.ground_points_topic} "
                    f"({ground_count} pts) + {self.obstacle_points_topic} "
                    f"({obstacle_count} pts)"
                )
            else:
                summary += (
                    " (point clouds not republished -- publish_point_clouds "
                    "is false; read the .npz directly with numpy if you "
                    "need the raw points, see module docstring)"
                )

            self.get_logger().info(summary)

        except Exception as exc:  # noqa: BLE001 - report, don't crash
            self.get_logger().error(
                f"terrain_map_server_node: {self.map_path} loaded but malformed "
                f"(missing/bad field?): {exc}"
            )

    def _publish_saved_cloud(self, data, key: str, pub, stamp, frame_id: str) -> int:
        """Publish one saved point cloud array (ground_points or
        obstacle_points) if present in the .npz; returns the point count
        published (0 if the key is missing, e.g. an older save format).
        Only called when publish_point_clouds is true.
        """
        if key not in data.files:
            self.get_logger().warning(
                f"terrain_map_server_node: saved map has no '{key}' (older "
                f"save format?) -- skipping that cloud's republish."
            )
            return 0

        points = data[key].astype(np.float32)

        header = Header()
        header.stamp = stamp
        header.frame_id = frame_id

        pub.publish(create_weighted_cloud(header, points))
        return len(points)


def main(args=None):
    rclpy.init(args=args)

    node = TerrainMapServerNode()

    try:
        # Keep the node (and its transient-local publishers) alive so late
        # subscribers still get the map -- see module docstring.
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()