"""Shared, vectorized point-cloud filtering primitives.

Extracted from rover_lidar/lidar_processing_node.py's crop/voxel/outlier
filter methods so both the lidar branch and the stereo branch of the
perception pipeline (diagram's "preprocessing_node") can reuse identical,
already-tested filtering logic instead of maintaining two copies with
subtly different behavior. Each sensor still gets its own ROS2 parameters
(noise characteristics differ between lidar and stereo depth), but the
math lives in exactly one place.

Points are carried as an (N, 4) float32 numpy array: x, y, z, weight.
`weight` (0..1) expresses how much a point should be trusted -- see
stereo_pointcloud_node.py for how it's computed on the stereo branch.
Lidar points don't originate with a weight (the real Livox driver has no
such field); pointcloud_preprocessing_node fills in weight=1.0 for any
cloud that doesn't already have one, so everything downstream of it can
assume 4 columns unconditionally.
"""

import numpy as np
from scipy.spatial import cKDTree

import sensor_msgs_py.point_cloud2 as pc2
from sensor_msgs.msg import PointField


WEIGHTED_FIELDS = [
    PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
    PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
    PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
    PointField(name="weight", offset=12, datatype=PointField.FLOAT32, count=1),
]


def create_weighted_cloud(header, points: np.ndarray):
    """(N, 4) float32 array of x, y, z, weight -> PointCloud2.

    create_cloud_xyz32 only supports 3 fields, so the 4th ("weight") field
    needs an explicit PointField layout -- this is that layout, in one
    place, so every node that publishes a weighted cloud does it identically.
    """
    return pc2.create_cloud(header, WEIGHTED_FIELDS, points)


def read_weighted_points(msg) -> np.ndarray:
    """PointCloud2 with x, y, z, weight fields -> (N, 4) float32 array."""
    return pc2.read_points_numpy(
        msg, field_names=("x", "y", "z", "weight"), skip_nans=True
    ).astype(np.float32)


def crop_filter(
    points: np.ndarray,
    min_x: float, max_x: float,
    min_y: float, max_y: float,
    min_z: float, max_z: float,
) -> np.ndarray:
    """Keep only points inside an axis-aligned region of interest.

    Works on any (N, >=3) array -- only columns 0/1/2 (x/y/z) are used for
    the bounds check; any extra columns (e.g. weight) are carried through
    unchanged on the rows that pass.
    """

    if len(points) == 0:
        return points

    mask = (
        (points[:, 0] >= min_x) & (points[:, 0] <= max_x) &
        (points[:, 1] >= min_y) & (points[:, 1] <= max_y) &
        (points[:, 2] >= min_z) & (points[:, 2] <= max_z)
    )

    return points[mask]


def voxel_grid_filter(points: np.ndarray, voxel_size: float) -> np.ndarray:
    """Downsample by merging points that fall into the same voxel.

    Expects (N, 4): x, y, z, weight. The merged point's position is the
    weight-weighted average of the points in that voxel (so a handful of
    confident points can outweigh a larger number of low-confidence ones);
    its weight is the mean weight of its contributors. Voxel *indices* are
    computed from x/y/z only -- weight must never leak into the spatial
    binning.
    """

    if len(points) == 0:
        return points

    xyz = points[:, :3].astype(np.float64)
    weight = points[:, 3].astype(np.float64)

    voxel_indices = np.floor(xyz / voxel_size).astype(np.int64)

    _, inverse, counts = np.unique(
        voxel_indices, axis=0, return_inverse=True, return_counts=True
    )
    inverse = inverse.ravel()
    n_voxels = counts.shape[0]

    weight_sums = np.zeros(n_voxels, dtype=np.float64)
    np.add.at(weight_sums, inverse, weight)

    # Plain-mean fallback for the (rare) voxel where every contributing
    # point has ~0 weight -- avoids a divide-by-zero / silently dropping it.
    plain_xyz_sums = np.zeros((n_voxels, 3), dtype=np.float64)
    np.add.at(plain_xyz_sums, inverse, xyz)
    plain_mean_xyz = plain_xyz_sums / counts[:, None]

    weighted_xyz_sums = np.zeros((n_voxels, 3), dtype=np.float64)
    np.add.at(weighted_xyz_sums, inverse, xyz * weight[:, None])

    has_weight = weight_sums > 1e-9
    safe_weight_sums = np.where(has_weight, weight_sums, 1.0)
    mean_xyz = np.where(
        has_weight[:, None],
        weighted_xyz_sums / safe_weight_sums[:, None],
        plain_mean_xyz,
    )

    mean_weight = weight_sums / counts

    return np.concatenate(
        [mean_xyz, mean_weight[:, None]], axis=1
    ).astype(np.float32)


def radius_outlier_filter(
    points: np.ndarray,
    radius: float,
    min_neighbors: int,
) -> np.ndarray:
    """Drop points with too few neighbors within `radius` (KDTree-based).

    The neighbor search is purely spatial (x, y, z) -- weight is not a
    spatial dimension and must be excluded from the tree, otherwise two
    physically distant points with similar weight would count as
    "neighbors".
    """

    if len(points) == 0:
        return points

    xyz = points[:, :3]
    tree = cKDTree(xyz)

    neighbor_counts = tree.query_ball_point(
        xyz, r=radius, return_length=True
    )

    # -1 because a point always counts itself as a neighbor.
    mask = (neighbor_counts - 1) >= min_neighbors

    return points[mask]
