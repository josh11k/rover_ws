// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rover_perception_msgs:msg/TerrainGrid.idl
// generated code does not contain a copyright notice

#ifndef ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__STRUCT_H_
#define ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'info'
#include "nav_msgs/msg/detail/map_meta_data__struct.h"
// Member 'traversability'
// Member 'min_z'
// Member 'max_z'
// Member 'mean_z'
// Member 'roughness'
// Member 'plane_slope_deg'
// Member 'point_count'
// Member 'total_weight'
#include "rosidl_runtime_c/primitives_sequence.h"

/// Struct defined in msg/TerrainGrid in the package rover_perception_msgs.
/**
  * Per-cell terrain statistics, published alongside the collapsed
  * traversability cost already available on nav_msgs/OccupancyGrid
  * (rover_perception's /terrain/traversability_grid).
  *
  * Same grid layout as that OccupancyGrid: row-major, index = iy * width + ix,
  * same `info` (resolution/width/height/origin), so cells line up 1:1 and can
  * be correlated by index between the two topics.
  *
  * Cells with less than `min_points_per_cell` *effective* points (see
  * total_weight below) use NaN for every float field and 0 for point_count /
  * total_weight -- this mirrors the OccupancyGrid's -1 ("unknown") convention
  * for that same cell, but with a per-field "no data" marker instead of one
  * shared sentinel value, since these are continuous quantities rather than a
  * bounded 0-100 cost.
 */
typedef struct rover_perception_msgs__msg__TerrainGrid
{
  std_msgs__msg__Header header;
  nav_msgs__msg__MapMetaData info;
  /// same values/semantics as OccupancyGrid.data
  rosidl_runtime_c__int8__Sequence traversability;
  rosidl_runtime_c__float__Sequence min_z;
  rosidl_runtime_c__float__Sequence max_z;
  rosidl_runtime_c__float__Sequence mean_z;
  rosidl_runtime_c__float__Sequence roughness;
  rosidl_runtime_c__float__Sequence plane_slope_deg;
  /// raw number of points that fell in the cell
  rosidl_runtime_c__int32__Sequence point_count;
  /// sum of per-point weight/confidence in the
  /// cell -- this (not point_count) is what gates
  /// whether a cell counts as "known" terrain,
  /// see rover_perception/terrain_analysis.py
  rosidl_runtime_c__float__Sequence total_weight;
} rover_perception_msgs__msg__TerrainGrid;

// Struct for a sequence of rover_perception_msgs__msg__TerrainGrid.
typedef struct rover_perception_msgs__msg__TerrainGrid__Sequence
{
  rover_perception_msgs__msg__TerrainGrid * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rover_perception_msgs__msg__TerrainGrid__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__STRUCT_H_
