"""Split the fused point cloud into ground vs. obstacle points, per (x,y)
tile, *before* gridding -- runs between global_pointcloud_fusion_node and
obstacle_grid_node. See chat history for the full design discussion; short
version below.

Why this exists
----------------
build_elevation_grid() (terrain_analysis.py) blends every point in a grid
cell into one set of stats (min/max/mean z, plane fit) regardless of
whether those points came from the actual floor or from a ceiling/shelf/
wall. In narrow/enclosed spaces that corrupts the floor estimate -- a cell
under a low shelf gets a huge min/max z spread and reads as "obstacle" even
though the floor under it is fine.

Persistent per-tile point buffer (moved here from obstacle_grid_node)
------------------------------------------------------------------------
This used to live in obstacle_grid_node (a rolling per-cell point buffer so
the published grid built up coverage across a pan sweep instead of only
reflecting the latest instant). It's been moved *here*, one stage earlier,
so the clustering below also benefits from more accumulated points per tile
instead of just whatever a single incoming message happens to contain --
important at a fine 20cm tile size, where a single message often only has 0
-2 points in a given tile. obstacle_grid_node no longer buffers anything
itself; it just grids whatever ground_points arrives, which is already the
accumulated/reclassified picture.

Buffers are raw (pre-classification) points, one `deque(maxlen=
max_points_per_cell)` per tile -- oldest point dropped first once full, a
rolling window, not a periodic hard reset.

Buffer-only during the scan; classify + publish on demand (redesigned
2026-09)
-----------------------------------------------------------------------------
Used to classify and republish the accumulated ground/obstacle clouds on a
periodic timer (publish_rate_hz) throughout the scan. That timer got
removed: at the intended scan sizes (60x60m, fine tiles -- see chat) the
accumulated clouds only grow over the course of a scan, so a *periodic*
full reclassify-and-republish meant repeating (and growing) work every
single tick for the entire scan -- CPU for the concatenation, memory churn
building a fresh array each tick, and an ever-larger published message,
continuously, not just once. That cascaded downstream too:
obstacle_grid_node's cloud_callback re-runs build_elevation_grid() over
whatever arrives on ground_points, so a continuously growing input meant a
continuously growing per-message cost there as well.

Since the intended workflow is a one-time, non-real-time-critical scan
(mast builds one detailed map, then perception goes quiet -- see chat),
none of that periodic work is actually needed while the scan is running.
cloud_callback() now does *only* the cheap, already-vectorized buffering
(_buffer_points()) -- no clustering, no publishing, no growing cost during
the scan itself, no matter how long it runs or how much area it covers.

Classification + publishing now happens exactly once, on demand, via a new
std_srvs/srv/Trigger service:

    ros2 service call /finalize_ground_segmentation std_srvs/srv/Trigger {}

Call this once, right after the scan is done, while the pipeline is still
ON (it needs the live subscription/publishers -- see _finalize_callback).
It reclassifies every tile touched since the last call (dirty-tile cache,
unchanged logic, just no longer timer-driven) and publishes the full
accumulated ground_points/obstacle_points clouds once, using transient-
local QoS so obstacle_grid_node -- or anything else subscribed at the time,
or subscribing shortly after -- reliably receives that one message. Calling
it again later (e.g. mid-scan, if you want an interim look) works fine too:
it just reclassifies whatever's newly dirty since the previous call and
republishes the current full picture.

Trade-off accepted deliberately: there's no live RViz preview of
ground/obstacle points building up *during* the scan anymore (that's what
the removed timer gave you). Given the scan isn't watched frame-by-frame in
real time anyway, that's fine -- see chat. If you want an occasional check
mid-scan, just call finalize_ground_segmentation yourself whenever you like
and look at the result; nothing stops you from calling it more than once.

Pairs with obstacle_grid_node's auto_save_on_compute parameter: since
obstacle_grid_node's cloud_callback now typically only fires once per scan
(exactly when this finalize service publishes), enabling
auto_save_on_compute there means calling finalize_ground_segmentation is,
in practice, the one command that ends the scan -- it triggers
classification here, which triggers gridding there, which then saves to
disk automatically. See obstacle_grid_node's module docstring.

Compute-load optimizations (buffering side, unchanged)
---------------------------------------------------------
Two, on top of the smaller per-tile buffer cap:

1. Dirty-tile tracking: only tiles that received new points since the last
   finalize call get re-clustered when finalize runs. Untouched tiles keep
   their last computed ground/obstacle split (self.tile_classification
   cache) instead of being redone from scratch.
2. Vectorized bucket-grouping when sorting new points into buffers (same
   sort + np.diff boundary trick build_elevation_grid() uses), so the
   Python-level loop runs once per *tile touched this message*, not once
   per point.

Clustering algorithm (per dirty tile, no plane fitting -- see chat for why
that was dropped)
-----------------------------------------------------------------------------
Tiles use the exact same (ix, iy) indexing convention as
terrain_analysis.build_elevation_grid() / obstacle_grid_node, at
grid_resolution/grid_size_x/grid_size_y -- deliberately kept in sync via the
launch file's `grid_resolution`/`grid_size` arguments so ground-segmentation
tiles line up 1:1 with the final elevation-grid cells.

For each dirty tile's buffered points:
  1. Sort by z.
  2. Split into clusters wherever the z-gap to the next point exceeds
     z_gap_threshold (default 0.20 m).
  3. Sum each cluster's point *weight* (not raw count -- low-confidence far/
     dark stereo points need to accumulate more of them before being
     trusted, same convention as obstacle_grid_node's total_weight gate).
  4. Starting from the lowest cluster and working up, take the first one
     whose summed weight >= min_ground_weight -- that's "ground" for this
     tile; all its points go to ground_points. Every other point in the
     tile (other clusters, or a tile where no cluster clears the bar) goes
     to obstacle_points.

What this deliberately does NOT do: detect walls directly. A wall
continuous with the floor (no z-gap) ends up entirely in one cluster and
gets passed through as "ground". That's intentional -- build_elevation_grid()
/compute_traversability() (unchanged) already flags such a cell via its huge
height_diff (min_z to max_z), and bleeds a "blocked" verdict into the
immediately adjacent floor cell(s) too via the mean_z step-to-neighbor
check, giving a small safety margin around the wall footprint for free.

Points outside the grid bounds (ix/iy out of range) are dropped entirely --
never buffered, never published either way.

Tuned 2026-09 for the one-time detailed pre-deployment scan
-------------------------------------------------------------
max_points_per_cell raised 150 -> 2000. During the earlier 10x10m bring-up
testing there was eviction pressure to worry about (many small tiles,
wanted to bound per-tile memory tightly). For the one-time build, more
buffered points per tile means a *more* reliable ground/obstacle split
(less chance the rolling window evicts the very points that would have
cleared min_ground_weight), and the scan has time to let the buffer fill --
there's no ongoing real-time budget being protected here. At 60x60m /
0.20m tiles (~90,000 tiles), worst case *all* tiles full is still only
~90,000 * 2000 * 4 floats * 4 bytes =~ 2.9 GB -- in practice nowhere near
that, since occupied tiles during a scan are a small fraction of the full
grid (only cells the sensors actually saw). Re-tune down if real memory use
on the Jetson gets tight.

Live coverage percentage (added 2026-09) -- NOT the same kind of timer as
the one removed above
-----------------------------------------------------------------------------
To let you eyeball progress *during* the scan without paying the
classify+concatenate+republish cost the redesign above removed, a small,
separate, genuinely-cheap timer publishes what fraction of the mapped area
currently has "enough" buffered points to be trustworthy:

    coverage_topic (default /perception/scan_coverage_pct, std_msgs/Float32)
    coverage_min_points (default 200) -- a cell counts as "covered" once its
        buffer holds at least this many raw points (this is a coverage/
        density check, independent of ground/obstacle classification --
        deliberately simpler and cheaper than that).
    coverage_publish_rate_hz (default 1.0)

This is safe to run continuously, unlike the removed timer, because the
work involved is fundamentally different: counting how many
self.cell_buffers entries have len(buf) >= coverage_min_points is an O(1)
length check per already-buffered tile (deques track their own length --
no array is built, nothing is sorted or clustered, no point cloud is
concatenated or published). At ~90,000 possible tiles worst case, that's a
dict-values scan with a comparison each -- microseconds to low
milliseconds, not remotely comparable to the per-tick cost the periodic
classify+publish timer used to have. Percentage is relative to the full
grid_width*grid_height cell count (the whole mapped area), not just tiles
touched so far, so it reads 0% at the start of a scan and approaches 100%
as coverage completes.
"""

from collections import deque

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy

from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header, Float32
from std_srvs.srv import Trigger
from rover_control_msgs.msg import OperationalModeSettings

from rover_perception.pointcloud_filters import (
    create_weighted_cloud,
    read_weighted_points,
)


DEFAULTS = {
    "input_topic": "/perception/global_points",
    "ground_topic": "/perception/ground_points",
    "obstacle_topic": "/perception/obstacle_points",
    "state_topic": "/operational_mode/settings",
    # This node sits right after global_pointcloud_fusion_node, same as
    # obstacle_grid_node -- follows the same OperationalModeSettings field
    # so both turn on/off together.
    "state_field": "make_global_pointcloud",

    # Must match obstacle_grid_node's grid_resolution/grid_size_x/grid_size_y
    # -- see launch file, where grid_resolution and grid_size are shared
    # launch arguments passed to both nodes so they can't drift out of sync.
    # These node-level values (10.0) are only the standalone-run fallback;
    # the launch file always overrides them explicitly (default 60.0).
    "grid_resolution": 0.20,
    "grid_size_x": 10.0,
    "grid_size_y": 10.0,

    # New cluster starts when the z-gap to the next point (sorted by z,
    # within one tile) exceeds this.
    "z_gap_threshold": 0.20,

    # Minimum summed point *weight* (not raw count) for a tile's lowest
    # cluster to be trusted as ground -- see module docstring.
    "min_ground_weight": 2.0,

    # Rolling per-tile buffer cap. Raised 2026-09 from 150 (the original
    # 10x10m bring-up value, chosen to bound memory tightly during testing)
    # to 2000 for the one-time detailed pre-deployment scan -- see module
    # docstring "Tuned 2026-09" section for the full reasoning and the
    # worst-case memory estimate at 60x60m.
    "max_points_per_cell": 2000,

    # Live coverage percentage -- see module docstring "Live coverage
    # percentage" section. Cheap, safe to run continuously, unrelated to
    # the removed classify+publish timer.
    "coverage_topic": "/perception/scan_coverage_pct",
    "coverage_min_points": 200,
    "coverage_publish_rate_hz": 1.0,
}


class GroundSegmentationNode(Node):

    def __init__(self):
        super().__init__("ground_segmentation_node")

        self._declare_parameters()
        self._load_parameters()
        self.state = "OFF"

        self.sub = None
        self.ground_pub = None
        self.obstacle_pub = None
        self.coverage_pub = None
        self.coverage_timer = None

        self.grid_width = int(self.grid_size_x / self.grid_resolution)
        self.grid_height = int(self.grid_size_y / self.grid_resolution)

        self.state_sub = self.create_subscription(
            OperationalModeSettings,
            self.state_topic,
            self.state_callback,
            10,
        )

        # Unconditional -- see module docstring "Buffer-only during the
        # scan; classify + publish on demand" section. Only actually usable
        # while ON (ground_pub/obstacle_pub exist); _finalize_callback
        # checks for that and reports a clear error otherwise.
        self.finalize_srv = self.create_service(
            Trigger, "finalize_ground_segmentation", self._finalize_callback,
        )

    def state_callback(self, msg):
        if not self.state_field:
            self.get_logger().error(
                "state_field parameter is not set -- this "
                "ground_segmentation_node instance doesn't know which "
                "OperationalModeSettings field to follow. Staying OFF. Set "
                "'state_field' explicitly in the launch file.",
                throttle_duration_sec=10.0,
            )
            return

        self.state = getattr(msg, self.state_field, "OFF")

        if self.state == "OFF":
            self.get_logger().info("ground_segmentation_node: OFF")

            if self.sub is not None:
                self.destroy_subscription(self.sub)
                self.sub = None
            if self.ground_pub is not None:
                self.destroy_publisher(self.ground_pub)
                self.ground_pub = None
            if self.obstacle_pub is not None:
                self.destroy_publisher(self.obstacle_pub)
                self.obstacle_pub = None
            if self.coverage_pub is not None:
                self.destroy_publisher(self.coverage_pub)
                self.coverage_pub = None
            if self.coverage_timer is not None:
                self.coverage_timer.destroy()
                self.coverage_timer = None

        elif self.state == "ON":
            self.get_logger().info("ground_segmentation_node: ON")

            self.sub = self.create_subscription(
                PointCloud2,
                self.input_topic,
                self.cloud_callback,
                10,
            )

            # Transient-local: finalize_ground_segmentation publishes at
            # most occasionally (once, typically, at the end of a scan --
            # see module docstring), so a subscriber (obstacle_grid_node,
            # RViz2) that starts up or subscribes slightly after that call
            # still reliably gets the last published cloud.
            cloud_qos = QoSProfile(
                depth=1,
                durability=DurabilityPolicy.TRANSIENT_LOCAL,
                reliability=ReliabilityPolicy.RELIABLE,
            )
            self.ground_pub = self.create_publisher(
                PointCloud2,
                self.ground_topic,
                cloud_qos,
            )
            self.obstacle_pub = self.create_publisher(
                PointCloud2,
                self.obstacle_topic,
                cloud_qos,
            )

            # Plain volatile QoS is fine here -- only the latest percentage
            # matters, nothing needs replaying to late subscribers. See
            # module docstring "Live coverage percentage" section.
            self.coverage_pub = self.create_publisher(
                Float32,
                self.coverage_topic,
                10,
            )

            # Fresh state every time this turns ON -- see module docstring.
            self.cell_buffers: dict = {}
            self.dirty_tiles: set = set()
            self.tile_classification: dict = {}
            self._last_frame_id = None

            self.coverage_timer = self.create_timer(
                1.0 / self.coverage_publish_rate_hz, self._publish_coverage,
            )

            self.get_logger().info(
                f"ground_segmentation_node: buffering {self.input_topic} "
                f"({self.grid_width}x{self.grid_height} tiles @ "
                f"{self.grid_resolution} m, z_gap_threshold="
                f"{self.z_gap_threshold} m, min_ground_weight="
                f"{self.min_ground_weight}, max_points_per_cell="
                f"{self.max_points_per_cell}). Call the "
                f"finalize_ground_segmentation service when the scan is "
                f"done to classify and publish to {self.ground_topic} + "
                f"{self.obstacle_topic}. Live coverage % (cells with >= "
                f"{self.coverage_min_points} pts) on {self.coverage_topic} "
                f"@ {self.coverage_publish_rate_hz} Hz."
            )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    # ------------------------------------------------------------------
    # Subscription callback: buffer only. No clustering, no publishing --
    # see module docstring "Buffer-only during the scan" section.
    # ------------------------------------------------------------------
    def cloud_callback(self, msg: PointCloud2):
        try:
            self._last_frame_id = msg.header.frame_id
            points = read_weighted_points(msg)

            if points.size == 0:
                return

            self._buffer_points(points)

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"cloud_callback failed: {exc}")

    def _buffer_points(self, points: np.ndarray):
        """Sort incoming points into their tile's rolling buffer, marking
        each touched tile dirty. Vectorized tile-grouping (sort + np.diff
        boundaries, same trick build_elevation_grid() uses) so the Python
        loop below runs once per *touched tile*, not once per point.
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

        if not np.any(valid):
            return

        valid_idx = np.flatnonzero(valid)
        keys = ix[valid_idx] * self.grid_height + iy[valid_idx]

        order = np.argsort(keys, kind="stable")
        idx_sorted = valid_idx[order]
        keys_sorted = keys[order]

        boundaries = np.flatnonzero(np.diff(keys_sorted)) + 1
        starts = np.concatenate(([0], boundaries))
        ends = np.concatenate((boundaries, [len(keys_sorted)]))

        for start, end in zip(starts, ends):
            tile_idx = idx_sorted[start:end]
            key = (int(ix[tile_idx[0]]), int(iy[tile_idx[0]]))

            buf = self.cell_buffers.get(key)
            if buf is None:
                buf = deque(maxlen=self.max_points_per_cell)
                self.cell_buffers[key] = buf

            # One extend() call per touched tile, not one append() per
            # point.
            buf.extend(points[tile_idx])
            self.dirty_tiles.add(key)

    # ------------------------------------------------------------------
    # Trigger service: reclassify dirty tiles, reuse cached classification
    # for everything else, then publish the full accumulated ground/
    # obstacle clouds once. See module docstring "Buffer-only during the
    # scan; classify + publish on demand" section.
    # ------------------------------------------------------------------
    def _finalize_callback(self, request, response):
        if self.ground_pub is None or self.obstacle_pub is None:
            response.success = False
            response.message = (
                "ground_segmentation_node is OFF (or not yet turned ON) -- "
                "nothing to finalize. Call this while the pipeline is "
                "still ON, right after the scan finishes."
            )
            self.get_logger().warning(
                f"finalize_ground_segmentation: {response.message}"
            )
            return response

        try:
            for key in list(self.dirty_tiles):
                buf = self.cell_buffers.get(key)
                if not buf:
                    continue
                tile_points = np.array(buf, dtype=np.float32)
                self.tile_classification[key] = self._classify_tile(tile_points)

            self.dirty_tiles.clear()

            if not self.tile_classification:
                response.success = False
                response.message = (
                    "No points buffered yet -- nothing to classify or "
                    f"publish. Has anything arrived on {self.input_topic}?"
                )
                self.get_logger().warning(
                    f"finalize_ground_segmentation: {response.message}"
                )
                return response

            if self._last_frame_id is None:
                response.success = False
                response.message = "No frame_id seen yet -- nothing to publish."
                self.get_logger().warning(
                    f"finalize_ground_segmentation: {response.message}"
                )
                return response

            ground_parts = [
                g for g, _ in self.tile_classification.values() if len(g) > 0
            ]
            obstacle_parts = [
                o for _, o in self.tile_classification.values() if len(o) > 0
            ]

            header = self._make_header()

            ground_count = 0
            if ground_parts:
                ground_pts = np.concatenate(ground_parts, axis=0)
                self.ground_pub.publish(create_weighted_cloud(header, ground_pts))
                ground_count = len(ground_pts)

            obstacle_count = 0
            if obstacle_parts:
                obstacle_pts = np.concatenate(obstacle_parts, axis=0)
                self.obstacle_pub.publish(create_weighted_cloud(header, obstacle_pts))
                obstacle_count = len(obstacle_pts)

            response.success = True
            response.message = (
                f"Published {ground_count} ground points to "
                f"{self.ground_topic} and {obstacle_count} obstacle points "
                f"to {self.obstacle_topic} ({len(self.tile_classification)} "
                f"tiles classified total)."
            )
            self.get_logger().info(
                f"finalize_ground_segmentation: {response.message}"
            )

        except Exception as exc:  # noqa: BLE001 - report, don't crash
            response.success = False
            response.message = f"finalize_ground_segmentation failed: {exc}"
            self.get_logger().error(response.message)

        return response

    # ------------------------------------------------------------------
    # Cheap, always-on timer: percentage of the mapped area whose buffer
    # currently holds at least coverage_min_points raw points. See module
    # docstring "Live coverage percentage" section for why this is safe to
    # run continuously, unlike the classify+publish timer that got removed.
    # ------------------------------------------------------------------
    def _publish_coverage(self):
        try:
            total_cells = self.grid_width * self.grid_height
            if total_cells <= 0:
                return

            covered = sum(
                1 for buf in self.cell_buffers.values()
                if len(buf) >= self.coverage_min_points
            )

            pct = 100.0 * covered / total_cells

            msg = Float32()
            msg.data = pct
            self.coverage_pub.publish(msg)

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"_publish_coverage failed: {exc}")

    def _make_header(self):
        header = Header()
        header.stamp = self.get_clock().now().to_msg()
        header.frame_id = self._last_frame_id
        return header

    def _classify_tile(self, tile_points: np.ndarray):
        """Cluster one tile's buffered points by z-gap; return
        (ground_points, obstacle_points) -- see module docstring for the
        algorithm.
        """

        z_vals = tile_points[:, 2]
        order = np.argsort(z_vals, kind="stable")
        pts_sorted = tile_points[order]
        z_sorted = z_vals[order]

        if len(z_sorted) > 1:
            gaps = np.diff(z_sorted)
            cluster_starts = np.concatenate((
                [0], np.flatnonzero(gaps > self.z_gap_threshold) + 1,
            ))
        else:
            cluster_starts = np.array([0])
        cluster_ends = np.concatenate((cluster_starts[1:], [len(z_sorted)]))

        for c_start, c_end in zip(cluster_starts, cluster_ends):
            cluster_weight = float(np.sum(pts_sorted[c_start:c_end, 3]))
            if cluster_weight >= self.min_ground_weight:
                ground = pts_sorted[c_start:c_end]
                obstacle = np.concatenate(
                    [pts_sorted[:c_start], pts_sorted[c_end:]], axis=0
                )
                return ground, obstacle
            # Not enough weight -- try the next (higher) cluster up.

        # No cluster cleared the bar -- whole tile stays obstacle.
        return (
            np.empty((0, 4), dtype=np.float32),
            pts_sorted,
        )


def main(args=None):
    rclpy.init(args=args)

    node = GroundSegmentationNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()