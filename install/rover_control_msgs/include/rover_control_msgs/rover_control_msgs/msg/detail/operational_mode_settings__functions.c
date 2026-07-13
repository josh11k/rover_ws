// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from rover_control_msgs:msg/OperationalModeSettings.idl
// generated code does not contain a copyright notice
#include "rover_control_msgs/msg/detail/operational_mode_settings__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `stereo_cam`
// Member `mono_cam`
// Member `lidar`
#include "rosidl_runtime_c/string_functions.h"

bool
rover_control_msgs__msg__OperationalModeSettings__init(rover_control_msgs__msg__OperationalModeSettings * msg)
{
  if (!msg) {
    return false;
  }
  // stereo_cam
  if (!rosidl_runtime_c__String__init(&msg->stereo_cam)) {
    rover_control_msgs__msg__OperationalModeSettings__fini(msg);
    return false;
  }
  // mono_cam
  if (!rosidl_runtime_c__String__init(&msg->mono_cam)) {
    rover_control_msgs__msg__OperationalModeSettings__fini(msg);
    return false;
  }
  // lidar
  if (!rosidl_runtime_c__String__init(&msg->lidar)) {
    rover_control_msgs__msg__OperationalModeSettings__fini(msg);
    return false;
  }
  return true;
}

void
rover_control_msgs__msg__OperationalModeSettings__fini(rover_control_msgs__msg__OperationalModeSettings * msg)
{
  if (!msg) {
    return;
  }
  // stereo_cam
  rosidl_runtime_c__String__fini(&msg->stereo_cam);
  // mono_cam
  rosidl_runtime_c__String__fini(&msg->mono_cam);
  // lidar
  rosidl_runtime_c__String__fini(&msg->lidar);
}

bool
rover_control_msgs__msg__OperationalModeSettings__are_equal(const rover_control_msgs__msg__OperationalModeSettings * lhs, const rover_control_msgs__msg__OperationalModeSettings * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // stereo_cam
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->stereo_cam), &(rhs->stereo_cam)))
  {
    return false;
  }
  // mono_cam
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->mono_cam), &(rhs->mono_cam)))
  {
    return false;
  }
  // lidar
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->lidar), &(rhs->lidar)))
  {
    return false;
  }
  return true;
}

bool
rover_control_msgs__msg__OperationalModeSettings__copy(
  const rover_control_msgs__msg__OperationalModeSettings * input,
  rover_control_msgs__msg__OperationalModeSettings * output)
{
  if (!input || !output) {
    return false;
  }
  // stereo_cam
  if (!rosidl_runtime_c__String__copy(
      &(input->stereo_cam), &(output->stereo_cam)))
  {
    return false;
  }
  // mono_cam
  if (!rosidl_runtime_c__String__copy(
      &(input->mono_cam), &(output->mono_cam)))
  {
    return false;
  }
  // lidar
  if (!rosidl_runtime_c__String__copy(
      &(input->lidar), &(output->lidar)))
  {
    return false;
  }
  return true;
}

rover_control_msgs__msg__OperationalModeSettings *
rover_control_msgs__msg__OperationalModeSettings__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__msg__OperationalModeSettings * msg = (rover_control_msgs__msg__OperationalModeSettings *)allocator.allocate(sizeof(rover_control_msgs__msg__OperationalModeSettings), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rover_control_msgs__msg__OperationalModeSettings));
  bool success = rover_control_msgs__msg__OperationalModeSettings__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rover_control_msgs__msg__OperationalModeSettings__destroy(rover_control_msgs__msg__OperationalModeSettings * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rover_control_msgs__msg__OperationalModeSettings__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rover_control_msgs__msg__OperationalModeSettings__Sequence__init(rover_control_msgs__msg__OperationalModeSettings__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__msg__OperationalModeSettings * data = NULL;

  if (size) {
    data = (rover_control_msgs__msg__OperationalModeSettings *)allocator.zero_allocate(size, sizeof(rover_control_msgs__msg__OperationalModeSettings), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rover_control_msgs__msg__OperationalModeSettings__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rover_control_msgs__msg__OperationalModeSettings__fini(&data[i - 1]);
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
rover_control_msgs__msg__OperationalModeSettings__Sequence__fini(rover_control_msgs__msg__OperationalModeSettings__Sequence * array)
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
      rover_control_msgs__msg__OperationalModeSettings__fini(&array->data[i]);
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

rover_control_msgs__msg__OperationalModeSettings__Sequence *
rover_control_msgs__msg__OperationalModeSettings__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__msg__OperationalModeSettings__Sequence * array = (rover_control_msgs__msg__OperationalModeSettings__Sequence *)allocator.allocate(sizeof(rover_control_msgs__msg__OperationalModeSettings__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rover_control_msgs__msg__OperationalModeSettings__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rover_control_msgs__msg__OperationalModeSettings__Sequence__destroy(rover_control_msgs__msg__OperationalModeSettings__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rover_control_msgs__msg__OperationalModeSettings__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rover_control_msgs__msg__OperationalModeSettings__Sequence__are_equal(const rover_control_msgs__msg__OperationalModeSettings__Sequence * lhs, const rover_control_msgs__msg__OperationalModeSettings__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rover_control_msgs__msg__OperationalModeSettings__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rover_control_msgs__msg__OperationalModeSettings__Sequence__copy(
  const rover_control_msgs__msg__OperationalModeSettings__Sequence * input,
  rover_control_msgs__msg__OperationalModeSettings__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rover_control_msgs__msg__OperationalModeSettings);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rover_control_msgs__msg__OperationalModeSettings * data =
      (rover_control_msgs__msg__OperationalModeSettings *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rover_control_msgs__msg__OperationalModeSettings__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rover_control_msgs__msg__OperationalModeSettings__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rover_control_msgs__msg__OperationalModeSettings__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
