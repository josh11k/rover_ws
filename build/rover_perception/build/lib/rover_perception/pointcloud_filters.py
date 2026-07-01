"""Shared, vectorized point-cloud filtering primitives.

Extracted from rover_lidar/lidar_processing_node.py's crop/voxel/outlier
filter methods so both the lidar branch and the stereo branch of the
perception pipeline (diagram's "preprocessing_node") can reuse identical,
already-tested filtering logic instead of maintaining two copies with
subtly different behavior. Each sensor still gets its own ROS2 parameters
(noise characteristics differ between lidar and stereo depth), but the
math lives in exactly one place.

All functions take/return an (N, 3) float32 numpy array of XYZ points.
"""

import numpy as np
from scipy.spatial import cKDTree


def crop_filter(
    points: np.ndarray,
    min_x: float, max_x: float,
    min_y: float, max_y: float,
    min_z: float, max_z: float,
) -> np.ndarray:
    """Keep only points inside an axis-aligned region of interest."""

    if len(points) == 0:
        return points

    mask = (
        (points[:, 0] >= min_x) & (points[:, 0] <= max_x) &
        (points[:, 1] >= min_y) & (points[:, 1] <= max_y) &
        (points[:, 2] >= min_z) & (points[:, 2] <= max_z)
    )

    return points[mask]


def voxel_grid_filter(points: np.ndarray, voxel_size: float) -> np.ndarray:
    """Downsample by averaging points that fall into the same voxel."""

    if len(points) == 0:
        return points

    voxel_indices = np.floor(points / voxel_size).astype(np.int64)

    _, inverse, counts = np.unique(
        voxel_indices, axis=0, return_inverse=True, return_counts=True
    )
    inverse = inverse.ravel()

    n_voxels = counts.shape[0]
    sums = np.zeros((n_voxels, 3), dtype=np.float64)
    np.add.at(sums, inverse, points.astype(np.float64))

    means = sums / counts[:, None]

    return means.astype(np.float32)


def radius_outlier_filter(
    points: np.ndarray,
    radius: float,
    min_neighbors: int,
) -> np.ndarray:
    """Drop points with too few neighbors within `radius` (KDTree-based)."""

    if len(points) == 0:
        return points

    tree = cKDTree(points)

    neighbor_counts = tree.query_ball_point(
        points, r=radius, return_length=True
    )

    # -1 because a point always counts itself as a neighbor.
    mask = (neighbor_counts - 1) >= min_neighbors

    return points[mask]
