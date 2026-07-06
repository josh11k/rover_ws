// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from rover_perception_msgs:msg/LedDetectionArray.idl
// generated code does not contain a copyright notice
#include "rover_perception_msgs/msg/detail/led_detection_array__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/detail/header__functions.h"
// Member `detections`
#include "rover_perception_msgs/msg/detail/led_detection__functions.h"

bool
rover_perception_msgs__msg__LedDetectionArray__init(rover_perception_msgs__msg__LedDetectionArray * msg)
{
  if (!msg) {
    return false;
  }
  // header
  if (!std_msgs__msg__Header__init(&msg->header)) {
    rover_perception_msgs__msg__LedDetectionArray__fini(msg);
    return false;
  }
  // detections
  if (!rover_perception_msgs__msg__LedDetection__Sequence__init(&msg->detections, 0)) {
    rover_perception_msgs__msg__LedDetectionArray__fini(msg);
    return false;
  }
  return true;
}

void
rover_perception_msgs__msg__LedDetectionArray__fini(rover_perception_msgs__msg__LedDetectionArray * msg)
{
  if (!msg) {
    return;
  }
  // header
  std_msgs__msg__Header__fini(&msg->header);
  // detections
  rover_perception_msgs__msg__LedDetection__Sequence__fini(&msg->detections);
}

bool
rover_perception_msgs__msg__LedDetectionArray__are_equal(const rover_perception_msgs__msg__LedDetectionArray * lhs, const rover_perception_msgs__msg__LedDetectionArray * rhs)
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
  // detections
  if (!rover_perception_msgs__msg__LedDetection__Sequence__are_equal(
      &(lhs->detections), &(rhs->detections)))
  {
    return false;
  }
  return true;
}

bool
rover_perception_msgs__msg__LedDetectionArray__copy(
  const rover_perception_msgs__msg__LedDetectionArray * input,
  rover_perception_msgs__msg__LedDetectionArray * output)
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
  // detections
  if (!rover_perception_msgs__msg__LedDetection__Sequence__copy(
      &(input->detections), &(output->detections)))
  {
    return false;
  }
  return true;
}

rover_perception_msgs__msg__LedDetectionArray *
rover_perception_msgs__msg__LedDetectionArray__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_perception_msgs__msg__LedDetectionArray * msg = (rover_perception_msgs__msg__LedDetectionArray *)allocator.allocate(sizeof(rover_perception_msgs__msg__LedDetectionArray), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rover_perception_msgs__msg__LedDetectionArray));
  bool success = rover_perception_msgs__msg__LedDetectionArray__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rover_perception_msgs__msg__LedDetectionArray__destroy(rover_perception_msgs__msg__LedDetectionArray * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rover_perception_msgs__msg__LedDetectionArray__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rover_perception_msgs__msg__LedDetectionArray__Sequence__init(rover_perception_msgs__msg__LedDetectionArray__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_perception_msgs__msg__LedDetectionArray * data = NULL;

  if (size) {
    data = (rover_perception_msgs__msg__LedDetectionArray *)allocator.zero_allocate(size, sizeof(rover_perception_msgs__msg__LedDetectionArray), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rover_perception_msgs__msg__LedDetectionArray__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rover_perception_msgs__msg__LedDetectionArray__fini(&data[i - 1]);
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
rover_perception_msgs__msg__LedDetectionArray__Sequence__fini(rover_perception_msgs__msg__LedDetectionArray__Sequence * array)
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
      rover_perception_msgs__msg__LedDetectionArray__fini(&array->data[i]);
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

rover_perception_msgs__msg__LedDetectionArray__Sequence *
rover_perception_msgs__msg__LedDetectionArray__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_perception_msgs__msg__LedDetectionArray__Sequence * array = (rover_perception_msgs__msg__LedDetectionArray__Sequence *)allocator.allocate(sizeof(rover_perception_msgs__msg__LedDetectionArray__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rover_perception_msgs__msg__LedDetectionArray__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rover_perception_msgs__msg__LedDetectionArray__Sequence__destroy(rover_perception_msgs__msg__LedDetectionArray__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rover_perception_msgs__msg__LedDetectionArray__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rover_perception_msgs__msg__LedDetectionArray__Sequence__are_equal(const rover_perception_msgs__msg__LedDetectionArray__Sequence * lhs, const rover_perception_msgs__msg__LedDetectionArray__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rover_perception_msgs__msg__LedDetectionArray__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rover_perception_msgs__msg__LedDetectionArray__Sequence__copy(
  const rover_perception_msgs__msg__LedDetectionArray__Sequence * input,
  rover_perception_msgs__msg__LedDetectionArray__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rover_perception_msgs__msg__LedDetectionArray);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rover_perception_msgs__msg__LedDetectionArray * data =
      (rover_perception_msgs__msg__LedDetectionArray *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rover_perception_msgs__msg__LedDetectionArray__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rover_perception_msgs__msg__LedDetectionArray__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rover_perception_msgs__msg__LedDetectionArray__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
