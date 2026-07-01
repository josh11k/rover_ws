"""Elevation-grid / traversability analysis, extracted from
rover_lidar/lidar_processing_node.py so it can be reused against a fused
(lidar + stereo) global point cloud instead of raw lidar-only points.

This is a straight port of the vectorized aggregation + plane-fit logic that
already existed and worked well in the lidar-only pipeline -- the algorithm
itself is unchanged, only the input source changes (fused cloud instead of
/livox/points directly).
"""

import math

import numpy as np


def build_elevation_grid(
    points: np.ndarray,
    grid_resolution: float,
    grid_size_x: float,
    grid_size_y: float,
    grid_width: int,
    grid_height: int,
    min_points_for_plane_fit: int,
) -> dict:
    """Aggregate points into (ix, iy) grid cells with per-cell stats."""

    grid = {}

    if len(points) == 0:
        return grid

    ix = np.floor((points[:, 0] + grid_size_x / 2.0) / grid_resolution).astype(np.int64)
    iy = np.floor((points[:, 1] + grid_size_y / 2.0) / grid_resolution).astype(np.int64)

    valid = (ix >= 0) & (ix < grid_width) & (iy >= 0) & (iy < grid_height)
    ix, iy, pts = ix[valid], iy[valid], points[valid]

    if len(pts) == 0:
        return grid

    keys = ix * grid_height + iy
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

        roughness, plane_slope_deg = _fit_plane_roughness_and_slope(
            cell_pts, min_points_for_plane_fit
        )

        grid[key] = {
            "min_z": min_z,
            "max_z": max_z,
            "mean_z": mean_z,
            "roughness": roughness,
            "plane_slope_deg": plane_slope_deg,
            "point_count": point_count,
        }

    return grid


def _fit_plane_roughness_and_slope(cell_points: np.ndarray, min_points_for_plane_fit: int):
    """Fit z = a*x + b*y + c per cell; return (roughness, slope_deg)."""

    z_vals = cell_points[:, 2]

    if len(cell_points) < min_points_for_plane_fit:
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


def compute_max_step_to_neighbor(elevation: dict, ix: int, iy: int) -> float:
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


def compute_local_slope_deg(
    elevation: dict, ix: int, iy: int, grid_resolution: float
) -> float:
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
        horizontal_distance = grid_resolution * math.sqrt(dx * dx + dy * dy)

        slope_rad = math.atan2(dz, horizontal_distance)
        slope_deg = math.degrees(slope_rad)

        max_slope = max(max_slope, slope_deg)

    return max_slope


def compute_traversability(
    elevation: dict,
    grid_width: int,
    grid_height: int,
    grid_resolution: float,
    max_step_height: float,
    max_roughness: float,
    max_slope_deg: float,
    min_points_per_cell: int,
) -> np.ndarray:
    """Turn per-cell elevation stats into an occupancy-style cost grid."""

    grid_data = np.full((grid_height, grid_width), -1, dtype=np.int8)

    for key, cell in elevation.items():
        ix, iy = key

        height_diff = cell["max_z"] - cell["min_z"]
        roughness = cell["roughness"]
        point_count = cell["point_count"]

        neighbor_slope_deg = compute_local_slope_deg(
            elevation, ix, iy, grid_resolution
        )
        slope_deg = max(neighbor_slope_deg, cell["plane_slope_deg"])

        max_step_to_neighbor = compute_max_step_to_neighbor(elevation, ix, iy)

        if point_count < min_points_per_cell:
            cost = -1

        elif height_diff > max_step_height:
            cost = 100

        elif max_step_to_neighbor > max_step_height:
            cost = 100

        elif roughness > max_roughness:
            cost = 80

        elif slope_deg > max_slope_deg:
            cost = 80

        else:
            step_cost = min(1.0, max_step_to_neighbor / max_step_height)
            rough_cost = min(1.0, roughness / max_roughness)
            slope_cost = min(1.0, slope_deg / max_slope_deg)
            height_cost = min(1.0, height_diff / max_step_height)

            cost = int(
                60 * max(step_cost, rough_cost, slope_cost, height_cost)
            )

        grid_data[iy, ix] = cost

    return grid_data
