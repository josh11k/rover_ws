// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from rover_perception_msgs:msg/TerrainGrid.idl
// generated code does not contain a copyright notice
#include "rover_perception_msgs/msg/detail/terrain_grid__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `info`
#include "nav_msgs/msg/detail/map_meta_data__functions.h"
// Member `traversability`
// Member `min_z`
// Member `max_z`
// Member `mean_z`
// Member `roughness`
// Member `plane_slope_deg`
// Member `point_count`
// Member `total_weight`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

bool
rover_perception_msgs__msg__TerrainGrid__init(rover_perception_msgs__msg__TerrainGrid * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    rover_perception_msgs__msg__TerrainGrid__fini(msg);
    return false;
  }
  // info
  if (!nav_msgs__msg__MapMetaData__init(&msg->info)) {
    rover_perception_msgs__msg__TerrainGrid__fini(msg);
    return false;
  }
  // traversability
  if (!rosidl_runtime_c__int8__Sequence__init(&msg->traversability, 0)) {
    rover_perception_msgs__msg__TerrainGrid__fini(msg);
    return false;
  }
  // min_z
  if (!rosidl_runtime_c__float__Sequence__init(&msg->min_z, 0)) {
    rover_perception_msgs__msg__TerrainGrid__fini(msg);
    return false;
  }
  // max_z
  if (!rosidl_runtime_c__float__Sequence__init(&msg->max_z, 0)) {
    rover_perception_msgs__msg__TerrainGrid__fini(msg);
    return false;
  }
  // mean_z
  if (!rosidl_runtime_c__float__Sequence__init(&msg->mean_z, 0)) {
    rover_perception_msgs__msg__TerrainGrid__fini(msg);
    return false;
  }
  // roughness
  if (!rosidl_runtime_c__float__Sequence__init(&msg->roughness, 0)) {
    rover_perception_msgs__msg__TerrainGrid__fini(msg);
    return false;
  }
  // plane_slope_deg
  if (!rosidl_runtime_c__float__Sequence__init(&msg->plane_slope_deg, 0)) {
    rover_perception_msgs__msg__TerrainGrid__fini(msg);
    return false;
  }
  // point_count
  if (!rosidl_runtime_c__int32__Sequence__init(&msg->point_count, 0)) {
    rover_perception_msgs__msg__TerrainGrid__fini(msg);
    return false;
  }
  // total_weight
  if (!rosidl_runtime_c__float__Sequence__init(&msg->total_weight, 0)) {
    rover_perception_msgs__msg__TerrainGrid__fini(msg);
    return false;
  }
  return true;
}

void
rover_perception_msgs__msg__TerrainGrid__fini(rover_perception_msgs__msg__TerrainGrid * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // info
  nav_msgs__msg__MapMetaData__fini(&msg->info);
  // traversability
  rosidl_runtime_c__int8__Sequence__fini(&msg->traversability);
  // min_z
  rosidl_runtime_c__float__Sequence__fini(&msg->min_z);
  // max_z
  rosidl_runtime_c__float__Sequence__fini(&msg->max_z);
  // mean_z
  rosidl_runtime_c__float__Sequence__fini(&msg->mean_z);
  // roughness
  rosidl_runtime_c__float__Sequence__fini(&msg->roughness);
  // plane_slope_deg
  rosidl_runtime_c__float__Sequence__fini(&msg->plane_slope_deg);
  // point_count
  rosidl_runtime_c__int32__Sequence__fini(&msg->point_count);
  // total_weight
  rosidl_runtime_c__float__Sequence__fini(&msg->total_weight);
}

bool
rover_perception_msgs__msg__TerrainGrid__are_equal(const rover_perception_msgs__msg__TerrainGrid * lhs, const rover_perception_msgs__msg__TerrainGrid * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__are_equal(
      &(lhs->header), &(rhs->header)))
  {
    return false;
  }
  // info
  if (!nav_msgs__msg__MapMetaData__are_equal(
      &(lhs->info), &(rhs->info)))
  {
    return false;
  }
  // traversability
  if (!rosidl_runtime_c__int8__Sequence__are_equal(
      &(lhs->traversability), &(rhs->traversability)))
  {
    return false;
  }
  // min_z
  if (!rosidl_runtime_c__float__Sequence__are_equal(
      &(lhs->min_z), &(rhs->min_z)))
  {
    return false;
  }
  // max_z
  if (!rosidl_runtime_c__float__Sequence__are_equal(
      &(lhs->max_z), &(rhs->max_z)))
  {
    return false;
  }
  // mean_z
  if (!rosidl_runtime_c__float__Sequence__are_equal(
      &(lhs->mean_z), &(rhs->mean_z)))
  {
    return false;
  }
  // roughness
  if (!rosidl_runtime_c__float__Sequence__are_equal(
      &(lhs->roughness), &(rhs->roughness)))
  {
    return false;
  }
  // plane_slope_deg
  if (!rosidl_runtime_c__float__Sequence__are_equal(
      &(lhs->plane_slope_deg), &(rhs->plane_slope_deg)))
  {
    return false;
  }
  // point_count
  if (!rosidl_runtime_c__int32__Sequence__are_equal(
      &(lhs->point_count), &(rhs->point_count)))
  {
    return false;
  }
  // total_weight
  if (!rosidl_runtime_c__float__Sequence__are_equal(
      &(lhs->total_weight), &(rhs->total_weight)))
  {
    return false;
  }
  return true;
}

bool
rover_perception_msgs__msg__TerrainGrid__copy(
  const rover_perception_msgs__msg__TerrainGrid * input,
  rover_perception_msgs__msg__TerrainGrid * output)
{
  if (!input || !output) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__copy(
      &(input->header), &(output->header)))
  {
    return false;
  }
  // info
  if (!nav_msgs__msg__MapMetaData__copy(
      &(input->info), &(output->info)))
  {
    return false;
  }
  // traversability
  if (!rosidl_runtime_c__int8__Sequence__copy(
      &(input->traversability), &(output->traversability)))
  {
    return false;
  }
  // min_z
  if (!rosidl_runtime_c__float__Sequence__copy(
      &(input->min_z), &(output->min_z)))
  {
    return false;
  }
  // max_z
  if (!rosidl_runtime_c__float__Sequence__copy(
      &(input->max_z), &(output->max_z)))
  {
    return false;
  }
  // mean_z
  if (!rosidl_runtime_c__float__Sequence__copy(
      &(input->mean_z), &(output->mean_z)))
  {
    return false;
  }
  // roughness
  if (!rosidl_runtime_c__float__Sequence__copy(
      &(input->roughness), &(output->roughness)))
  {
    return false;
  }
  // plane_slope_deg
  if (!rosidl_runtime_c__float__Sequence__copy(
      &(input->plane_slope_deg), &(output->plane_slope_deg)))
  {
    return false;
  }
  // point_count
  if (!rosidl_runtime_c__int32__Sequence__copy(
      &(input->point_count), &(output->point_count)))
  {
    return false;
  }
  // total_weight
  if (!rosidl_runtime_c__float__Sequence__copy(
      &(input->total_weight), &(output->total_weight)))
  {
    return false;
  }
  return true;
}

rover_perception_msgs__msg__TerrainGrid *
rover_perception_msgs__msg__TerrainGrid__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_perception_msgs__msg__TerrainGrid * msg = (rover_perception_msgs__msg__TerrainGrid *)allocator.allocate(sizeof(rover_perception_msgs__msg__TerrainGrid), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rover_perception_msgs__msg__TerrainGrid));
  bool success = rover_perception_msgs__msg__TerrainGrid__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rover_perception_msgs__msg__TerrainGrid__destroy(rover_perception_msgs__msg__TerrainGrid * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rover_perception_msgs__msg__TerrainGrid__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rover_perception_msgs__msg__TerrainGrid__Sequence__init(rover_perception_msgs__msg__TerrainGrid__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_perception_msgs__msg__TerrainGrid * data = NULL;

  if (size) {
    data = (rover_perception_msgs__msg__TerrainGrid *)allocator.zero_allocate(size, sizeof(rover_perception_msgs__msg__TerrainGrid), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rover_perception_msgs__msg__TerrainGrid__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rover_perception_msgs__msg__TerrainGrid__fini(&data[i - 1]);
      }
      allocator.deallocate(data, allocator.state);
      return false;
    }
  }
  array->data = data;
  array->size = size;
  array->capacity = size;
  return true;
}

void
rover_perception_msgs__msg__TerrainGrid__Sequence__fini(rover_perception_msgs__msg__TerrainGrid__Sequence * array)
{
  if (!array) {
    return;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();

  if (array->data) {
    // ensure that data and capacity values are consistent
    assert(array->capacity > 0);
    // finalize all array elements
    for (size_t i = 0; i < array->capacity; ++i) {
      rover_perception_msgs__msg__TerrainGrid__fini(&array->data[i]);
    }
    allocator.deallocate(array->data, allocator.state);
    array->data = NULL;
    array->size = 0;
    array->capacity = 0;
  } else {
    // ensure that data, size, and capacity values are consistent
    assert(0 == array->size);
    assert(0 == array->capacity);
  }
}

rover_perception_msgs__msg__TerrainGrid__Sequence *
rover_perception_msgs__msg__TerrainGrid__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_perception_msgs__msg__TerrainGrid__Sequence * array = (rover_perception_msgs__msg__TerrainGrid__Sequence *)allocator.allocate(sizeof(rover_perception_msgs__msg__TerrainGrid__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rover_perception_msgs__msg__TerrainGrid__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rover_perception_msgs__msg__TerrainGrid__Sequence__destroy(rover_perception_msgs__msg__TerrainGrid__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rover_perception_msgs__msg__TerrainGrid__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rover_perception_msgs__msg__TerrainGrid__Sequence__are_equal(const rover_perception_msgs__msg__TerrainGrid__Sequence * lhs, const rover_perception_msgs__msg__TerrainGrid__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rover_perception_msgs__msg__TerrainGrid__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rover_perception_msgs__msg__TerrainGrid__Sequence__copy(
  const rover_perception_msgs__msg__TerrainGrid__Sequence * input,
  rover_perception_msgs__msg__TerrainGrid__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rover_perception_msgs__msg__TerrainGrid);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rover_perception_msgs__msg__TerrainGrid * data =
      (rover_perception_msgs__msg__TerrainGrid *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rover_perception_msgs__msg__TerrainGrid__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rover_perception_msgs__msg__TerrainGrid__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rover_perception_msgs__msg__TerrainGrid__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
