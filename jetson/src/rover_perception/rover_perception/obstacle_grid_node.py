"""grid_node + identify_obstacles_node combined.

Consumes the ground-segmented point cloud (see ground_segmentation_node --
lidar + stereo, fused and already split into ground vs. obstacle points,
already in mast_base_link -- the mast's own quasi-static frame, only moves
under real mast lean, not with pan/tilt) and publishes an OccupancyGrid
traversability map, reusing the elevation-grid / traversability algorithm
from terrain_analysis.py (ported from rover_lidar/lidar_processing_node.py).

Diagram nodes covered: grid_node ("convert points into blocks") and
identify_obstacles_node ("finds local height differences, which could mean
obstacle").

Fixed 2026-09: no longer buffers points itself. This used to keep its own
persistent per-cell point buffer to build up coverage across a pan sweep
(see chat) -- that responsibility has moved to ground_segmentation_node,
one stage earlier, so its ground-classification clustering also benefits
from the accumulated history (fine tiles otherwise see too few points per
message to cluster reliably). ground_segmentation_node's ground_points
output is already the accumulated/reclassified picture, so this node is
back to being a simple stateless function of "whatever's in the latest
message" -- see that node's module docstring for the buffering design.

Redesigned 2026-09: ground_segmentation_node no longer publishes on a
periodic timer -- it only buffers during a scan and publishes once, on
demand, via its finalize_ground_segmentation service (see that node's
module docstring). Practically, that means this node's cloud_callback now
typically only fires *once* per scan too, right when finalize is called --
not continuously. That made it worth adding an auto-save option here (see
"Map persistence" below), since a single compute-then-save is now the
common case instead of a rare, separately-triggered event.

Map persistence (added 2026-09)
----------------------------------
Modeled on Nav2's map_saver/map_server pattern: this node's own state is
never touched by "saving" -- saving is just a snapshot of the last
successfully computed grid to disk, so the live pipeline can keep running
(or be switched off) independently of whether/when someone saves.

- Every successful cloud_callback() run caches its computed traversability
  grid + terrain stats + frame_id + the raw ground_points cloud it just
  graded (self._last_traversability / self._last_stats /
  self._last_frame_id / self._last_ground_points).
- A second, separate subscription (obstacle_points_topic, defaults to
  ground_segmentation_node's /perception/obstacle_points) exists purely to
  keep a matching snapshot of the latest obstacle cloud
  (self._last_obstacle_points) -- this node never grids or otherwise uses
  obstacle points, it only tags along here so saving can persist ground and
  obstacle points as two clearly separate arrays, not mixed together. If no
  obstacle cloud has ever arrived (e.g. an entirely open, obstacle-free
  scan), this stays an empty (0, 4) array rather than None, so saving never
  fails because of it.
- The actual save logic lives in _save_map(), shared by two triggers:
    1. A std_srvs/srv/Trigger service, save_terrain_map, created in
       __init__ unconditionally (NOT gated by ON/OFF -- you can save right
       after switching perception off at the end of a scan):
           ros2 service call /save_terrain_map std_srvs/srv/Trigger {}
    2. The auto_save_on_compute parameter (default false). When true,
       cloud_callback() calls _save_map() itself immediately after every
       successful computation -- no separate service call needed. Given
       ground_segmentation_node's finalize-on-demand redesign (see above),
       enabling this means calling finalize_ground_segmentation is, in
       practice, the one command that ends a scan: it triggers
       classification there, which triggers gridding + auto-save here.
       Left off by default because it writes to disk on *every* successful
       compute -- fine for the intended "fires once per scan" case, but
       would mean repeated disk writes if this node's input ever becomes
       continuous again (e.g. during earlier bring-up-style testing against
       a live, periodically-publishing source).
  Either path writes the cached snapshot to map_save_path via
  numpy.savez_compressed(), with ground_points and obstacle_points stored
  under their own separate keys (each an (N, 4) x/y/z/weight array -- same
  layout pointcloud_filters.read_weighted_points()/create_weighted_cloud()
  use everywhere else in this package). Fails cleanly (success = False, a
  message explaining why) if no grid has been computed yet.
- terrain_map_server_node.py (separate file, standalone -- not started by
  this launch file) loads that .npz back and republishes the grid, stats,
  and (optionally) both point clouds, all once, with transient-local QoS,
  for use after the live pipeline is off. See that node's own module
  docstring.

Usage: once you've finished a scan, either call the service yourself:
    ros2 service call /save_terrain_map std_srvs/srv/Trigger {}
or set auto_save_on_compute:=true and just call
ground_segmentation_node's finalize_ground_segmentation service -- the
save then happens automatically as a side effect of gridding its output.
"""

import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid, MapMetaData
from geometry_msgs.msg import Pose
from std_srvs.srv import Trigger

from rover_perception_msgs.msg import TerrainGrid
from rover_control_msgs.msg import OperationalModeSettings

from rover_perception.pointcloud_filters import read_weighted_points
from rover_perception.terrain_analysis import (
    build_elevation_grid,
    compute_traversability,
    flatten_elevation_grid,
)


DEFAULTS = {
    # Fixed 2026-09: was "/perception/global_points" -- now consumes
    # ground_segmentation_node's output instead of the raw fused cloud, so
    # ceiling/shelf/wall points no longer corrupt the elevation-grid stats
    # for a cell. See ground_segmentation_node's module docstring.
    "points_topic": "/perception/ground_points",

    # Added 2026-09: subscribed to purely so saving can persist obstacle
    # points too, kept clearly separate from ground_points -- see module
    # docstring "Map persistence" section. Not used for gridding.
    "obstacle_points_topic": "/perception/obstacle_points",

    "traversability_topic": "/terrain/traversability_grid",
    "terrain_stats_topic": "/terrain/terrain_grid_stats",
    "output_frame_id": "mast_base_link",
    "state_topic": "/operational_mode/settings",

    "grid_resolution": 1.0,
    "grid_size_x": 10.0,
    "grid_size_y": 10.0,

    "max_step_height": 0.20,
    "max_roughness": 0.10,
    "max_slope_deg": 18.0,
    "min_points_per_cell": 2,
    "min_points_for_plane_fit": 4,

    # Where saving writes the finished map (.npz). Directory must already
    # exist -- saving fails with a clear message otherwise rather than
    # trying to create it. Overridden by the launch file's map_save_path
    # argument in normal use.
    "map_save_path": "/home/team/rover_maps/terrain_map.npz",

    # Added 2026-09: automatically save (same logic as the save_terrain_map
    # service) right after every successful cloud_callback() computation --
    # see module docstring "Map persistence" section. Off by default.
    "auto_save_on_compute": False,
}


class ObstacleGridNode(Node):

    def __init__(self):
        super().__init__("obstacle_grid_node")

        self._declare_parameters()
        self._load_parameters()
        self.state = "OFF"

        self.sub = None
        self.obstacle_sub = None
        self.pub = None
        self.stats_pub = None

        # Last successfully computed result, cached for saving -- see
        # module docstring "Map persistence" section. Populated on every
        # successful cloud_callback() run regardless of whether anyone ever
        # triggers a save; None until the first one lands.
        self._last_traversability = None
        self._last_stats = None
        self._last_frame_id = None
        self._last_info = None
        self._last_ground_points = None
        self._last_obstacle_points = None

        self.grid_width = int(self.grid_size_x / self.grid_resolution)
        self.grid_height = int(self.grid_size_y / self.grid_resolution)


        self.state_sub = self.create_subscription(
            OperationalModeSettings,
            self.state_topic,
            self.state_callback,
            10,
        )

        # Unconditional -- available whether the pipeline is currently ON
        # or OFF, so you can save right after switching perception off at
        # the end of a scan. See module docstring.
        self.save_srv = self.create_service(
            Trigger, "save_terrain_map", self._save_map_callback,
        )

    def state_callback(self, msg):

        self.state = msg.make_global_pointcloud

        if self.state == "OFF":

            self.get_logger().info(f"obstacle_grid_node: OFF")

            self.destroy_subscription(self.sub)
            self.destroy_subscription(self.obstacle_sub)
            self.destroy_publisher(self.pub)
            self.destroy_publisher(self.stats_pub)

            self.sub = None
            self.obstacle_sub = None
            self.pub = None
            self.stats_pub = None

        elif self.state == "ON":

            self.get_logger().info(f"obstacle_grid_node: ON")

            self.sub = self.create_subscription(
                PointCloud2,
                self.points_topic,
                self.cloud_callback,
                10,
            )

            # Ground truth for gridding is points_topic above -- this
            # second subscription exists only to keep a matching snapshot
            # of the latest obstacle cloud for saving. See module docstring
            # "Map persistence" section.
            self.obstacle_sub = self.create_subscription(
                PointCloud2,
                self.obstacle_points_topic,
                self._obstacle_cloud_callback,
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
                f"{self.grid_resolution} m; also watching "
                f"{self.obstacle_points_topic} for saving"
                + (
                    "; auto_save_on_compute is ON -- will save to "
                    f"{self.map_save_path} after every successful compute)"
                    if self.auto_save_on_compute
                    else ")"
                )
            )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def cloud_callback(self, msg: PointCloud2):
        try:
            points = read_weighted_points(msg)

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

            # Cache for saving -- see module docstring. Cached
            # unconditionally on every successful run, independent of
            # whether a save is ever triggered.
            self._last_traversability = traversability
            self._last_stats = stats
            self._last_frame_id = frame_id
            self._last_info = info
            self._last_ground_points = points

            # Added 2026-09 -- see module docstring "Map persistence"
            # section for why this defaults to off.
            if self.auto_save_on_compute:
                success, message = self._save_map()
                if success:
                    self.get_logger().info(f"auto_save_on_compute: {message}")
                else:
                    self.get_logger().error(f"auto_save_on_compute: {message}")

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"cloud_callback failed: {exc}")

    def _obstacle_cloud_callback(self, msg: PointCloud2):
        """Only used to keep a snapshot of the latest obstacle cloud for
        saving -- see module docstring "Map persistence" section. This node
        doesn't grid or otherwise use obstacle points; ground truth for
        gridding is cloud_callback()/points_topic above.
        """
        try:
            self._last_obstacle_points = read_weighted_points(msg)
        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"_obstacle_cloud_callback failed: {exc}")

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

    def _save_map_callback(self, request, response):
        """std_srvs/srv/Trigger handler for save_terrain_map. Thin wrapper
        around _save_map() -- see that method and module docstring "Map
        persistence" section.
        """
        response.success, response.message = self._save_map()

        if response.success:
            self.get_logger().info(f"save_terrain_map: {response.message}")
        else:
            self.get_logger().warning(f"save_terrain_map: {response.message}")

        return response

    def _save_map(self) -> tuple[bool, str]:
        """Core save logic, shared by the save_terrain_map service and
        auto_save_on_compute -- see module docstring "Map persistence"
        section. Writes the last successfully computed grid + stats +
        ground/obstacle point clouds to map_save_path as a compressed .npz
        -- see terrain_map_server_node.py, which loads this back. Returns
        (success, message); never raises.
        """
        if self._last_traversability is None or self._last_stats is None:
            return (
                False,
                "No terrain grid computed yet -- nothing to save. Is the "
                "pipeline ON and has a point cloud arrived on "
                f"{self.points_topic}?",
            )

        try:
            stats = self._last_stats

            # Obstacle points are optional (an entirely open, obstacle-free
            # scan may never see a message on obstacle_points_topic) --
            # fall back to an empty array rather than failing the save.
            # Ground points always exist alongside a computed grid, since
            # they come from the same message/topic that produced it.
            ground_points = self._last_ground_points
            obstacle_points = (
                self._last_obstacle_points
                if self._last_obstacle_points is not None
                else np.empty((0, 4), dtype=np.float32)
            )

            np.savez_compressed(
                self.map_save_path,
                traversability=self._last_traversability,
                min_z=stats["min_z"],
                max_z=stats["max_z"],
                mean_z=stats["mean_z"],
                roughness=stats["roughness"],
                plane_slope_deg=stats["plane_slope_deg"],
                point_count=stats["point_count"],
                total_weight=stats["total_weight"],
                # Kept as two clearly separate arrays (not concatenated)
                # so terrain_map_server_node -- or anything else reading
                # this file -- can tell ground and obstacle points apart
                # without needing a label column. Each is (N, 4): x, y, z,
                # weight -- the same layout read_weighted_points() /
                # create_weighted_cloud() use everywhere else.
                ground_points=ground_points,
                obstacle_points=obstacle_points,
                grid_resolution=self.grid_resolution,
                grid_size_x=self.grid_size_x,
                grid_size_y=self.grid_size_y,
                grid_width=self.grid_width,
                grid_height=self.grid_height,
                frame_id=self._last_frame_id,
            )

            return (
                True,
                f"Terrain map saved to {self.map_save_path} "
                f"({len(ground_points)} ground points, "
                f"{len(obstacle_points)} obstacle points)",
            )

        except Exception as exc:  # noqa: BLE001 - report, don't crash
            return False, f"Failed to save terrain map: {exc}"


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