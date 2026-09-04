// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from rover_control_msgs:msg/CurrentOperationalMode.idl
// generated code does not contain a copyright notice
#include "rover_control_msgs/msg/detail/current_operational_mode__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"


// Include directives for member types
// Member `mode`
#include "rosidl_runtime_c/string_functions.h"

bool
rover_control_msgs__msg__CurrentOperationalMode__init(rover_control_msgs__msg__CurrentOperationalMode * msg)
{
  if (!msg) {
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__init(&msg->mode)) {
    rover_control_msgs__msg__CurrentOperationalMode__fini(msg);
    return false;
  }
  return true;
}

void
rover_control_msgs__msg__CurrentOperationalMode__fini(rover_control_msgs__msg__CurrentOperationalMode * msg)
{
  if (!msg) {
    return;
  }
  // mode
  rosidl_runtime_c__String__fini(&msg->mode);
}

bool
rover_control_msgs__msg__CurrentOperationalMode__are_equal(const rover_control_msgs__msg__CurrentOperationalMode * lhs, const rover_control_msgs__msg__CurrentOperationalMode * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->mode), &(rhs->mode)))
  {
    return false;
  }
  return true;
}

bool
rover_control_msgs__msg__CurrentOperationalMode__copy(
  const rover_control_msgs__msg__CurrentOperationalMode * input,
  rover_control_msgs__msg__CurrentOperationalMode * output)
{
  if (!input || !output) {
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__copy(
      &(input->mode), &(output->mode)))
  {
    return false;
  }
  return true;
}

rover_control_msgs__msg__CurrentOperationalMode *
rover_control_msgs__msg__CurrentOperationalMode__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__msg__CurrentOperationalMode * msg = (rover_control_msgs__msg__CurrentOperationalMode *)allocator.allocate(sizeof(rover_control_msgs__msg__CurrentOperationalMode), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rover_control_msgs__msg__CurrentOperationalMode));
  bool success = rover_control_msgs__msg__CurrentOperationalMode__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rover_control_msgs__msg__CurrentOperationalMode__destroy(rover_control_msgs__msg__CurrentOperationalMode * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rover_control_msgs__msg__CurrentOperationalMode__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rover_control_msgs__msg__CurrentOperationalMode__Sequence__init(rover_control_msgs__msg__CurrentOperationalMode__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__msg__CurrentOperationalMode * data = NULL;

  if (size) {
    data = (rover_control_msgs__msg__CurrentOperationalMode *)allocator.zero_allocate(size, sizeof(rover_control_msgs__msg__CurrentOperationalMode), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rover_control_msgs__msg__CurrentOperationalMode__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rover_control_msgs__msg__CurrentOperationalMode__fini(&data[i - 1]);
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
rover_control_msgs__msg__CurrentOperationalMode__Sequence__fini(rover_control_msgs__msg__CurrentOperationalMode__Sequence * array)
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
      rover_control_msgs__msg__CurrentOperationalMode__fini(&array->data[i]);
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

rover_control_msgs__msg__CurrentOperationalMode__Sequence *
rover_control_msgs__msg__CurrentOperationalMode__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__msg__CurrentOperationalMode__Sequence * array = (rover_control_msgs__msg__CurrentOperationalMode__Sequence *)allocator.allocate(sizeof(rover_control_msgs__msg__CurrentOperationalMode__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rover_control_msgs__msg__CurrentOperationalMode__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rover_control_msgs__msg__CurrentOperationalMode__Sequence__destroy(rover_control_msgs__msg__CurrentOperationalMode__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rover_control_msgs__msg__CurrentOperationalMode__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rover_control_msgs__msg__CurrentOperationalMode__Sequence__are_equal(const rover_control_msgs__msg__CurrentOperationalMode__Sequence * lhs, const rover_control_msgs__msg__CurrentOperationalMode__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rover_control_msgs__msg__CurrentOperationalMode__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rover_control_msgs__msg__CurrentOperationalMode__Sequence__copy(
  const rover_control_msgs__msg__CurrentOperationalMode__Sequence * input,
  rover_control_msgs__msg__CurrentOperationalMode__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rover_control_msgs__msg__CurrentOperationalMode);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rover_control_msgs__msg__CurrentOperationalMode * data =
      (rover_control_msgs__msg__CurrentOperationalMode *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rover_control_msgs__msg__CurrentOperationalMode__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rover_control_msgs__msg__CurrentOperationalMode__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rover_control_msgs__msg__CurrentOperationalMode__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
