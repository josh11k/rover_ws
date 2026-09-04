# Per-cell terrain statistics, published alongside the collapsed
# traversability cost already available on nav_msgs/OccupancyGrid
# (rover_perception's /terrain/traversability_grid).
#
# Same grid layout as that OccupancyGrid: row-major, index = iy * width + ix,
# same `info` (resolution/width/height/origin), so cells line up 1:1 and can
# be correlated by index between the two topics.
#
# Cells with less than `min_points_per_cell` *effective* points (see
# total_weight below) use NaN for every float field and 0 for point_count /
# total_weight -- this mirrors the OccupancyGrid's -1 ("unknown") convention
# for that same cell, but with a per-field "no data" marker instead of one
# shared sentinel value, since these are continuous quantities rather than a
# bounded 0-100 cost.

std_msgs/Header header
nav_msgs/MapMetaData info

int8[]    traversability     # same values/semantics as OccupancyGrid.data
float32[] min_z
float32[] max_z
float32[] mean_z
float32[] roughness
float32[] plane_slope_deg
int32[]   point_count        # raw number of points that fell in the cell
float32[] total_weight       # sum of per-point weight/confidence in the
                              # cell -- this (not point_count) is what gates
                              # whether a cell counts as "known" terrain,
                              # see rover_perception/terrain_analysis.py
