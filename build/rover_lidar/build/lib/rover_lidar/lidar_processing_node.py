import math
from collections import defaultdict

import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import PointCloud2
from nav_msgs.msg import OccupancyGrid
from geometry_msgs.msg import Pose

import sensor_msgs_py.point_cloud2 as pc2


# =========================
# CONFIG
# =========================

POINTS_TOPIC = "/livox/points"
TRAVERSABILITY_TOPIC = "/terrain/traversability_grid"

GRID_RESOLUTION = 0.25  # meter pro grid cell
GRID_SIZE_X = 20.0      # meter
GRID_SIZE_Y = 20.0      # meter

MIN_X = -10.0
MAX_X = 10.0
MIN_Y = -10.0
MAX_Y = 10.0
MIN_Z = -2.0
MAX_Z = 3.0

VOXEL_SIZE = 0.20

OUTLIER_RADIUS = 0.50
MIN_NEIGHBORS = 2

MAX_STEP_HEIGHT = 0.20
MAX_ROUGHNESS = 0.10
MAX_SLOPE_DEG = 18.0
MIN_POINTS_PER_CELL = 2


class LidarProcessingNode(Node):
    def __init__(self):
        super().__init__("lidar_processing_node")

        self.pointcloud_sub = self.create_subscription(
            PointCloud2,
            POINTS_TOPIC,
            self.pointcloud_callback,
            10
        )

        self.trav_pub = self.create_publisher(
            OccupancyGrid,
            TRAVERSABILITY_TOPIC,
            10
        )

        self.grid_width = int(GRID_SIZE_X / GRID_RESOLUTION)
        self.grid_height = int(GRID_SIZE_Y / GRID_RESOLUTION)

        self.get_logger().info("LiDAR Processing Node started")

    def pointcloud_callback(self, msg: PointCloud2):
        points_structured = pc2.read_points(
            msg,
            field_names=("x", "y", "z"),
            skip_nans=True
        )

        raw_points = np.array(
            [
                [point["x"], point["y"], point["z"]]
                for point in points_structured
            ],
            dtype=np.float32
        )

        if raw_points.size == 0:
            self.get_logger().warn("Empty point cloud received")
            return

        cropped = self.crop_filter(raw_points)
        voxel = self.voxel_grid_filter(cropped)
        clean = self.radius_outlier_filter(voxel)

        elevation = self.build_elevation_grid(clean)
        traversability = self.compute_traversability(elevation)

        self.publish_occupancy_grid(traversability, msg.header.stamp)

        self.get_logger().info(
            f"Raw={len(raw_points)} | Crop={len(cropped)} | "
            f"Voxel={len(voxel)} | Clean={len(clean)}"
        )

    # =========================
    # 1. CROP / ROI FILTER
    # =========================

    def crop_filter(self, points: np.ndarray) -> np.ndarray:
        mask = (
            (points[:, 0] >= MIN_X) & (points[:, 0] <= MAX_X) &
            (points[:, 1] >= MIN_Y) & (points[:, 1] <= MAX_Y) &
            (points[:, 2] >= MIN_Z) & (points[:, 2] <= MAX_Z)
        )

        return points[mask]

    # =========================
    # 2. VOXEL GRID FILTER
    # =========================

    def voxel_grid_filter(self, points: np.ndarray) -> np.ndarray:
        if len(points) == 0:
            return points

        voxel_indices = np.floor(points / VOXEL_SIZE).astype(np.int32)
        voxel_dict = defaultdict(list)

        for idx, point in zip(map(tuple, voxel_indices), points):
            voxel_dict[idx].append(point)

        downsampled = []

        for voxel_points in voxel_dict.values():
            downsampled.append(np.mean(voxel_points, axis=0))

        return np.array(downsampled, dtype=np.float32)

    # =========================
    # 3. RADIUS OUTLIER REMOVAL
    # =========================

    def radius_outlier_filter(self, points: np.ndarray) -> np.ndarray:
        if len(points) == 0:
            return points

        filtered = []
        radius_sq = OUTLIER_RADIUS ** 2

        for i, p in enumerate(points):
            diff = points - p
            dist_sq = np.sum(diff * diff, axis=1)

            neighbor_count = np.sum(dist_sq < radius_sq) - 1

            if neighbor_count >= MIN_NEIGHBORS:
                filtered.append(p)

        return np.array(filtered, dtype=np.float32)

    # =========================
    # 4. ELEVATION GRID
    # =========================

    def build_elevation_grid(self, points: np.ndarray) -> dict:
        grid = {}

        for x, y, z in points:
            ix = int((x + GRID_SIZE_X / 2.0) / GRID_RESOLUTION)
            iy = int((y + GRID_SIZE_Y / 2.0) / GRID_RESOLUTION)

            if 0 <= ix < self.grid_width and 0 <= iy < self.grid_height:
                key = (ix, iy)

                if key not in grid:
                    grid[key] = {
                        "z_values": [],
                        "min_z": float(z),
                        "max_z": float(z),
                        "mean_z": float(z),
                        "roughness": 0.0,
                        "point_count": 0,
                    }

                cell = grid[key]

                cell["z_values"].append(float(z))
                cell["min_z"] = min(cell["min_z"], float(z))
                cell["max_z"] = max(cell["max_z"], float(z))

        for cell in grid.values():
            z_values = np.array(cell["z_values"])

            cell["mean_z"] = float(np.mean(z_values))
            cell["roughness"] = float(np.std(z_values))
            cell["point_count"] = len(z_values)

        return grid

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

            slope_deg = self.compute_local_slope_deg(elevation, ix, iy)
            max_step_to_neighbor = self.compute_max_step_to_neighbor(
                elevation,
                ix,
                iy
            )

            if point_count < MIN_POINTS_PER_CELL:
                cost = -1

            elif height_diff > MAX_STEP_HEIGHT:
                cost = 100

            elif max_step_to_neighbor > MAX_STEP_HEIGHT:
                cost = 100

            elif roughness > MAX_ROUGHNESS:
                cost = 80

            elif slope_deg > MAX_SLOPE_DEG:
                cost = 80

            else:
                step_cost = min(1.0, max_step_to_neighbor / MAX_STEP_HEIGHT)
                rough_cost = min(1.0, roughness / MAX_ROUGHNESS)
                slope_cost = min(1.0, slope_deg / MAX_SLOPE_DEG)
                height_cost = min(1.0, height_diff / MAX_STEP_HEIGHT)

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
            horizontal_distance = GRID_RESOLUTION * math.sqrt(dx * dx + dy * dy)

            slope_rad = math.atan2(dz, horizontal_distance)
            slope_deg = math.degrees(slope_rad)

            max_slope = max(max_slope, slope_deg)

        return max_slope

    # =========================
    # 6. PUBLISH OCCUPANCY GRID
    # =========================

    def publish_occupancy_grid(self, traversability: np.ndarray, stamp):
        msg = OccupancyGrid()

        msg.header.stamp = stamp
        msg.header.frame_id = "lidar_frame"

        msg.info.resolution = GRID_RESOLUTION
        msg.info.width = self.grid_width
        msg.info.height = self.grid_height

        msg.info.origin = Pose()
        msg.info.origin.position.x = -GRID_SIZE_X / 2.0
        msg.info.origin.position.y = -GRID_SIZE_Y / 2.0
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