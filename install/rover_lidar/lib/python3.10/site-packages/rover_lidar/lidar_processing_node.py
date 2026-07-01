import math

import numpy as np
from scipy.spatial import cKDTree

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Pose

import sensor_msgs_py.point_cloud2 as pc2


# =========================
# DEFAULT CONFIG
# (alle Werte sind jetzt zusätzlich als ROS2-Parameter
#  zur Laufzeit überschreibbar, siehe _declare_parameters)
# =========================

DEFAULTS = {
    "points_topic": "/livox/points",
    "traversability_topic": "/terrain/traversability_grid",
    "output_frame_id": "",  # leer = msg.header.frame_id der PointCloud übernehmen

    "grid_resolution": 0.25,   # meter pro grid cell
    "grid_size_x": 100.0,      # meter
    "grid_size_y": 100.0,      # meter

    "min_x": -50.0,
    "max_x": 50.0,
    "min_y": -50.0,
    "max_y": 50.0,
    "min_z": -10.0,
    "max_z": 10.0,

    "voxel_size": 0.20,

    "outlier_radius": 0.50,
    "min_neighbors": 2,

    "max_step_height": 0.20,
    "max_roughness": 0.10,
    "max_slope_deg": 18.0,
    "min_points_per_cell": 2,
    "min_points_for_plane_fit": 4,
}


class LidarProcessingNode(Node):
    def __init__(self):
        super().__init__("lidar_processing_node")

        self._declare_parameters()
        self._load_parameters()

        self.pointcloud_sub = self.create_subscription(
            PointCloud2,
            self.points_topic,
            self.pointcloud_callback,
            qos_profile_sensor_data,  # passt zu typischen LiDAR-Treiber-QoS (BEST_EFFORT)
        )

        self.trav_pub = self.create_publisher(
            OccupancyGrid,
            self.traversability_topic,
            10
        )

        self.grid_width = int(self.grid_size_x / self.grid_resolution)
        self.grid_height = int(self.grid_size_y / self.grid_resolution)

        self.get_logger().info("LiDAR Processing Node started")

    # =========================
    # PARAMETERS
    # =========================

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    # =========================
    # CALLBACK
    # =========================

    def pointcloud_callback(self, msg: PointCloud2):
        try:
            raw_points = pc2.read_points_numpy(
                msg,
                field_names=("x", "y", "z"),
                skip_nans=True,
            ).astype(np.float32)

            if raw_points.size == 0:
                self.get_logger().warn("Empty point cloud received")
                return

            cropped = self.crop_filter(raw_points)
            voxel = self.voxel_grid_filter(cropped)
            clean = self.radius_outlier_filter(voxel)

            elevation = self.build_elevation_grid(clean)
            traversability = self.compute_traversability(elevation)

            frame_id = self.output_frame_id or msg.header.frame_id or "lidar_frame"
            self.publish_occupancy_grid(traversability, msg.header.stamp, frame_id)

            self.get_logger().info(
                f"Raw={len(raw_points)} | Crop={len(cropped)} | "
                f"Voxel={len(voxel)} | Clean={len(clean)}"
            )

        except Exception as exc:  # noqa: BLE001 - Callback darf den Node nicht crashen
            self.get_logger().error(f"pointcloud_callback failed: {exc}")

    # =========================
    # 1. CROP / ROI FILTER
    # =========================

    def crop_filter(self, points: np.ndarray) -> np.ndarray:
        mask = (
            (points[:, 0] >= self.min_x) & (points[:, 0] <= self.max_x) &
            (points[:, 1] >= self.min_y) & (points[:, 1] <= self.max_y) &
            (points[:, 2] >= self.min_z) & (points[:, 2] <= self.max_z)
        )

        return points[mask]

    # =========================
    # 2. VOXEL GRID FILTER (vektorisiert)
    # =========================

    def voxel_grid_filter(self, points: np.ndarray) -> np.ndarray:
        if len(points) == 0:
            return points

        voxel_indices = np.floor(points / self.voxel_size).astype(np.int64)

        # Eindeutige Voxel-Zellen + Rückindex je Punkt -> Zelle
        _, inverse, counts = np.unique(
            voxel_indices, axis=0, return_inverse=True, return_counts=True
        )
        inverse = inverse.ravel()

        n_voxels = counts.shape[0]
        sums = np.zeros((n_voxels, 3), dtype=np.float64)
        np.add.at(sums, inverse, points.astype(np.float64))

        means = sums / counts[:, None]

        return means.astype(np.float32)

    # =========================
    # 3. RADIUS OUTLIER REMOVAL (KDTree, statt O(n^2))
    # =========================

    def radius_outlier_filter(self, points: np.ndarray) -> np.ndarray:
        if len(points) == 0:
            return points

        tree = cKDTree(points)

        # return_length=True liefert direkt die Anzahl der Nachbarn
        # (inkl. sich selbst) pro Punkt, ohne Python-seitige Listen.
        neighbor_counts = tree.query_ball_point(
            points, r=self.outlier_radius, return_length=True
        )

        # -1, weil der Punkt sich selbst immer als Nachbar mitzählt
        mask = (neighbor_counts - 1) >= self.min_neighbors

        return points[mask]

    # =========================
    # 4. ELEVATION GRID (vektorisierte Aggregation + Ebenenanpassung)
    # =========================

    def build_elevation_grid(self, points: np.ndarray) -> dict:
        grid = {}

        if len(points) == 0:
            return grid

        ix = np.floor((points[:, 0] + self.grid_size_x / 2.0) / self.grid_resolution).astype(np.int64)
        iy = np.floor((points[:, 1] + self.grid_size_y / 2.0) / self.grid_resolution).astype(np.int64)

        valid = (ix >= 0) & (ix < self.grid_width) & (iy >= 0) & (iy < self.grid_height)
        ix, iy, pts = ix[valid], iy[valid], points[valid]

        if len(pts) == 0:
            return grid

        keys = ix * self.grid_height + iy
        order = np.argsort(keys, kind="stable")
        keys_sorted = keys[order]
        pts_sorted = pts[order]
        ix_sorted = ix[order]
        iy_sorted = iy[order]

        boundaries = np.flatnonzero(np.diff(keys_sorted)) + 1
        starts = np.concatenate(([0], boundaries))
        ends = np.concatenate((boundaries, [len(keys_sorted)]))

        for start, end in zip(starts, ends):
            cell_pts = pts_sorted[start:end]
            z_vals = cell_pts[:, 2]
            key = (int(ix_sorted[start]), int(iy_sorted[start]))

            min_z = float(np.min(z_vals))
            max_z = float(np.max(z_vals))
            mean_z = float(np.mean(z_vals))
            point_count = len(z_vals)

            roughness, plane_slope_deg = self._fit_plane_roughness_and_slope(cell_pts)

            grid[key] = {
                "min_z": min_z,
                "max_z": max_z,
                "mean_z": mean_z,
                "roughness": roughness,
                "plane_slope_deg": plane_slope_deg,
                "point_count": point_count,
            }

        return grid

    def _fit_plane_roughness_and_slope(self, cell_points: np.ndarray):
        """Fittet z = a*x + b*y + c pro Zelle und liefert die Residual-Streuung
        (Roughness, unabhängig von der reinen Hangneigung) sowie die aus der
        Ebene abgeleitete Neigung in Grad. Fällt bei zu wenigen Punkten auf
        std(z) bzw. 0.0 Grad Hangneigung zurück."""

        z_vals = cell_points[:, 2]

        if len(cell_points) < self.min_points_for_plane_fit:
            return float(np.std(z_vals)), 0.0

        x = cell_points[:, 0]
        y = cell_points[:, 1]

        design = np.column_stack([x, y, np.ones_like(x)])

        try:
            coeffs, _, _, _ = np.linalg.lstsq(design, z_vals, rcond=None)
        except np.linalg.LinAlgError:
            return float(np.std(z_vals)), 0.0

        a, b, _c = coeffs
        predicted = design @ coeffs
        residuals = z_vals - predicted

        roughness = float(np.std(residuals))
        plane_slope_deg = float(math.degrees(math.atan(math.hypot(a, b))))

        return roughness, plane_slope_deg

    # =========================
    # 5. TRAVERSABILITY ANALYSIS
    # =========================

    def compute_traversability(self, elevation: dict) -> np.ndarray:
        grid_data = np.full(
            (self.grid_height, self.grid_width),
            -1,
            dtype=np.int8
        )

        for key, cell in elevation.items():
            ix, iy = key

            height_diff = cell["max_z"] - cell["min_z"]
            roughness = cell["roughness"]
            point_count = cell["point_count"]

            neighbor_slope_deg = self.compute_local_slope_deg(elevation, ix, iy)
            # Kombination aus Nachbarzellen-Gradient und lokaler Ebenenanpassung:
            # robust gegen Rauschen einzelner Nachbar-Mittelwerte UND gegen
            # echte Hangneigung innerhalb einer einzelnen Zelle.
            slope_deg = max(neighbor_slope_deg, cell["plane_slope_deg"])

            max_step_to_neighbor = self.compute_max_step_to_neighbor(
                elevation,
                ix,
                iy
            )

            if point_count < self.min_points_per_cell:
                cost = -1

            elif height_diff > self.max_step_height:
                cost = 100

            elif max_step_to_neighbor > self.max_step_height:
                cost = 100

            elif roughness > self.max_roughness:
                cost = 80

            elif slope_deg > self.max_slope_deg:
                cost = 80

            else:
                step_cost = min(1.0, max_step_to_neighbor / self.max_step_height)
                rough_cost = min(1.0, roughness / self.max_roughness)
                slope_cost = min(1.0, slope_deg / self.max_slope_deg)
                height_cost = min(1.0, height_diff / self.max_step_height)

                cost = int(
                    60 * max(
                        step_cost,
                        rough_cost,
                        slope_cost,
                        height_cost
                    )
                )

            grid_data[iy, ix] = cost

        return grid_data

    def compute_max_step_to_neighbor(self, elevation: dict, ix: int, iy: int) -> float:
        center_key = (ix, iy)

        if center_key not in elevation:
            return 0.0

        center_z = elevation[center_key]["mean_z"]
        max_step = 0.0

        for dx, dy in [
            (-1, 0), (1, 0),
            (0, -1), (0, 1),
            (-1, -1), (-1, 1),
            (1, -1), (1, 1),
        ]:
            n_key = (ix + dx, iy + dy)

            if n_key not in elevation:
                continue

            neighbor_z = elevation[n_key]["mean_z"]
            step = abs(center_z - neighbor_z)

            max_step = max(max_step, step)

        return max_step

    def compute_local_slope_deg(self, elevation: dict, ix: int, iy: int) -> float:
        center_key = (ix, iy)

        if center_key not in elevation:
            return 0.0

        center_z = elevation[center_key]["mean_z"]
        max_slope = 0.0

        for dx, dy in [
            (-1, 0), (1, 0),
            (0, -1), (0, 1),
            (-1, -1), (-1, 1),
            (1, -1), (1, 1),
        ]:
            n_key = (ix + dx, iy + dy)

            if n_key not in elevation:
                continue

            neighbor_z = elevation[n_key]["mean_z"]

            dz = abs(center_z - neighbor_z)
            horizontal_distance = self.grid_resolution * math.sqrt(dx * dx + dy * dy)

            slope_rad = math.atan2(dz, horizontal_distance)
            slope_deg = math.degrees(slope_rad)

            max_slope = max(max_slope, slope_deg)

        return max_slope

    # =========================
    # 6. PUBLISH OCCUPANCY GRID
    # =========================

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

        self.trav_pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = LidarProcessingNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()