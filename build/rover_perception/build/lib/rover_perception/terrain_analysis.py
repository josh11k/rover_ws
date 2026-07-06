"""Elevation-grid / traversability analysis, extracted from
rover_lidar/lidar_processing_node.py so it can be reused against a fused
(lidar + stereo) global point cloud instead of raw lidar-only points.

Points are (N, 4): x, y, z, weight (see pointcloud_filters.py). `weight`
(0..1) expresses per-point confidence -- low for far-away/low-light stereo
points, 1.0 for lidar points (no confidence model for lidar yet). It's used
in two places here: as a weighted mean/plane-fit instead of a plain one (so
low-confidence points are outweighed rather than treated equally), and as an
"effective point count" (`total_weight`) that gates whether a cell is
trusted at all -- a cell built only from far/dark stereo points needs many
more of them to pass the same bar as a cell with a couple of solid lidar
returns.
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
        xyz = cell_pts[:, :3]
        cell_weight = cell_pts[:, 3]
        z_vals = xyz[:, 2]
        key = (int(ix_sorted[start]), int(iy_sorted[start]))

        min_z = float(np.min(z_vals))
        max_z = float(np.max(z_vals))
        point_count = len(z_vals)
        total_weight = float(np.sum(cell_weight))

        if total_weight > 1e-9:
            mean_z = float(np.sum(z_vals * cell_weight) / total_weight)
        else:
            mean_z = float(np.mean(z_vals))

        roughness, plane_slope_deg = _fit_plane_roughness_and_slope(
            xyz, cell_weight, min_points_for_plane_fit
        )

        grid[key] = {
            "min_z": min_z,
            "max_z": max_z,
            "mean_z": mean_z,
            "roughness": roughness,
            "plane_slope_deg": plane_slope_deg,
            "point_count": point_count,
            "total_weight": total_weight,
        }

    return grid


def _fit_plane_roughness_and_slope(
    cell_xyz: np.ndarray, cell_weight: np.ndarray, min_points_for_plane_fit: int
):
    """Fit z = a*x + b*y + c per cell (weighted least squares); return
    (roughness, slope_deg). Low-weight points still count as *samples* for
    the min_points_for_plane_fit check (that's about numerical stability /
    degrees of freedom, not confidence) but contribute less to the fitted
    plane itself.
    """

    z_vals = cell_xyz[:, 2]

    if len(cell_xyz) < min_points_for_plane_fit:
        return float(np.std(z_vals)), 0.0

    x = cell_xyz[:, 0]
    y = cell_xyz[:, 1]

    design = np.column_stack([x, y, np.ones_like(x)])

    sqrt_w = np.sqrt(np.clip(cell_weight, 1e-6, None))
    design_weighted = design * sqrt_w[:, None]
    z_weighted = z_vals * sqrt_w

    try:
        coeffs, _, _, _ = np.linalg.lstsq(design_weighted, z_weighted, rcond=None)
    except np.linalg.LinAlgError:
        return float(np.std(z_vals)), 0.0

    a, b, _c = coeffs
    predicted = design @ coeffs
    residuals = z_vals - predicted

    roughness = float(np.std(residuals))
    plane_slope_deg = float(math.degrees(math.atan(math.hypot(a, b))))

    return roughness, plane_slope_deg


def flatten_elevation_grid(
    elevation: dict,
    grid_width: int,
    grid_height: int,
) -> dict:
    """Flatten the per-cell elevation dict into row-major
    (index = iy * grid_width + ix) arrays, one per statistic -- matches the
    layout `traversability.flatten()` already uses in obstacle_grid_node, so
    both can be published side by side and correlated by index.

    Cells with no data get NaN (float fields) / 0 (point_count / total_weight),
    instead of a shared sentinel like the traversability grid's -1, since
    these are continuous quantities rather than a bounded cost.
    """

    n = grid_width * grid_height

    min_z = np.full(n, np.nan, dtype=np.float32)
    max_z = np.full(n, np.nan, dtype=np.float32)
    mean_z = np.full(n, np.nan, dtype=np.float32)
    roughness = np.full(n, np.nan, dtype=np.float32)
    plane_slope_deg = np.full(n, np.nan, dtype=np.float32)
    point_count = np.zeros(n, dtype=np.int32)
    total_weight = np.zeros(n, dtype=np.float32)

    for (ix, iy), cell in elevation.items():
        idx = iy * grid_width + ix

        min_z[idx] = cell["min_z"]
        max_z[idx] = cell["max_z"]
        mean_z[idx] = cell["mean_z"]
        roughness[idx] = cell["roughness"]
        plane_slope_deg[idx] = cell["plane_slope_deg"]
        point_count[idx] = cell["point_count"]
        total_weight[idx] = cell["total_weight"]

    return {
        "min_z": min_z,
        "max_z": max_z,
        "mean_z": mean_z,
        "roughness": roughness,
        "plane_slope_deg": plane_slope_deg,
        "point_count": point_count,
        "total_weight": total_weight,
    }


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
    """Turn per-cell elevation stats into an occupancy-style cost grid.

    The "enough data to trust this cell" gate now compares against
    `total_weight` (sum of per-point confidence) instead of the raw point
    count -- a cell built from many low-confidence (far/dark) stereo points
    needs to accumulate the same effective weight as a cell with a couple
    of full-confidence returns before it's treated as known terrain.
    """

    grid_data = np.full((grid_height, grid_width), -1, dtype=np.int8)

    for key, cell in elevation.items():
        ix, iy = key

        height_diff = cell["max_z"] - cell["min_z"]
        roughness = cell["roughness"]
        total_weight = cell["total_weight"]

        neighbor_slope_deg = compute_local_slope_deg(
            elevation, ix, iy, grid_resolution
        )
        # Kombination aus Nachbarzellen-Gradient und lokaler Ebenenanpassung:
        # robust gegen Rauschen einzelner Nachbar-Mittelwerte UND gegen
        # echte Hangneigung innerhalb einer einzelnen Zelle.
        slope_deg = max(neighbor_slope_deg, cell["plane_slope_deg"])

        max_step_to_neighbor = compute_max_step_to_neighbor(elevation, ix, iy)

        if total_weight < min_points_per_cell:
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
