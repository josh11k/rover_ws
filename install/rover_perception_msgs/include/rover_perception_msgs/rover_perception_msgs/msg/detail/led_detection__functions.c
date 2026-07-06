// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from rover_perception_msgs:msg/LedDetection.idl
// generated code does not contain a copyright notice
#include "rover_perception_msgs/msg/detail/led_detection__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `bearing`
#include "geometry_msgs/msg/detail/vector3__functions.h"

bool
rover_perception_msgs__msg__LedDetection__init(rover_perception_msgs__msg__LedDetection * msg)
{
  if (!msg) {
    return false;
  }
  // pixel_u
  // pixel_v
  // area_px
  // color_r
  // color_g
  // color_b
  // bearing
  if (!geometry_msgs__msg__Vector3__init(&msg->bearing)) {
    rover_perception_msgs__msg__LedDetection__fini(msg);
    return false;
  }
  return true;
}

void
rover_perception_msgs__msg__LedDetection__fini(rover_perception_msgs__msg__LedDetection * msg)
{
  if (!msg) {
    return;
  }
  // pixel_u
  // pixel_v
  // area_px
  // color_r
  // color_g
  // color_b
  // bearing
  geometry_msgs__msg__Vector3__fini(&msg->bearing);
}

bool
rover_perception_msgs__msg__LedDetection__are_equal(const rover_perception_msgs__msg__LedDetection * lhs, const rover_perception_msgs__msg__LedDetection * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // pixel_u
  if (lhs->pixel_u != rhs->pixel_u) {
    return false;
  }
  // pixel_v
  if (lhs->pixel_v != rhs->pixel_v) {
    return false;
  }
  // area_px
  if (lhs->area_px != rhs->area_px) {
    return false;
  }
  // color_r
  if (lhs->color_r != rhs->color_r) {
    return false;
  }
  // color_g
  if (lhs->color_g != rhs->color_g) {
    return false;
  }
  // color_b
  if (lhs->color_b != rhs->color_b) {
    return false;
  }
  // bearing
  if (!geometry_msgs__msg__Vector3__are_equal(
      &(lhs->bearing), &(rhs->bearing)))
  {
    return false;
  }
  return true;
}

bool
rover_perception_msgs__msg__LedDetection__copy(
  const rover_perception_msgs__msg__LedDetection * input,
  rover_perception_msgs__msg__LedDetection * output)
{
  if (!input || !output) {
    return false;
  }
  // pixel_u
  output->pixel_u = input->pixel_u;
  // pixel_v
  output->pixel_v = input->pixel_v;
  // area_px
  output->area_px = input->area_px;
  // color_r
  output->color_r = input->color_r;
  // color_g
  output->color_g = input->color_g;
  // color_b
  output->color_b = input->color_b;
  // bearing
  if (!geometry_msgs__msg__Vector3__copy(
      &(input->bearing), &(output->bearing)))
  {
    return false;
  }
  return true;
}

rover_perception_msgs__msg__LedDetection *
rover_perception_msgs__msg__LedDetection__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_perception_msgs__msg__LedDetection * msg = (rover_perception_msgs__msg__LedDetection *)allocator.allocate(sizeof(rover_perception_msgs__msg__LedDetection), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rover_perception_msgs__msg__LedDetection));
  bool success = rover_perception_msgs__msg__LedDetection__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rover_perception_msgs__msg__LedDetection__destroy(rover_perception_msgs__msg__LedDetection * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rover_perception_msgs__msg__LedDetection__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rover_perception_msgs__msg__LedDetection__Sequence__init(rover_perception_msgs__msg__LedDetection__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_perception_msgs__msg__LedDetection * data = NULL;

  if (size) {
    data = (rover_perception_msgs__msg__LedDetection *)allocator.zero_allocate(size, sizeof(rover_perception_msgs__msg__LedDetection), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rover_perception_msgs__msg__LedDetection__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rover_perception_msgs__msg__LedDetection__fini(&data[i - 1]);
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
rover_perception_msgs__msg__LedDetection__Sequence__fini(rover_perception_msgs__msg__LedDetection__Sequence * array)
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
      rover_perception_msgs__msg__LedDetection__fini(&array->data[i]);
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

rover_perception_msgs__msg__LedDetection__Sequence *
rover_perception_msgs__msg__LedDetection__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_perception_msgs__msg__LedDetection__Sequence * array = (rover_perception_msgs__msg__LedDetection__Sequence *)allocator.allocate(sizeof(rover_perception_msgs__msg__LedDetection__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rover_perception_msgs__msg__LedDetection__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rover_perception_msgs__msg__LedDetection__Sequence__destroy(rover_perception_msgs__msg__LedDetection__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rover_perception_msgs__msg__LedDetection__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rover_perception_msgs__msg__LedDetection__Sequence__are_equal(const rover_perception_msgs__msg__LedDetection__Sequence * lhs, const rover_perception_msgs__msg__LedDetection__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rover_perception_msgs__msg__LedDetection__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rover_perception_msgs__msg__LedDetection__Sequence__copy(
  const rover_perception_msgs__msg__LedDetection__Sequence * input,
  rover_perception_msgs__msg__LedDetection__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rover_perception_msgs__msg__LedDetection);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rover_perception_msgs__msg__LedDetection * data =
      (rover_perception_msgs__msg__LedDetection *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rover_perception_msgs__msg__LedDetection__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rover_perception_msgs__msg__LedDetection__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rover_perception_msgs__msg__LedDetection__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
