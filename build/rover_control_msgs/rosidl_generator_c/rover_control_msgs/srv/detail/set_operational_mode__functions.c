// generated from rosidl_generator_c/resource/idl__functions.c.em
// with input from rover_control_msgs:srv/SetOperationalMode.idl
// generated code does not contain a copyright notice
#include "rover_control_msgs/srv/detail/set_operational_mode__functions.h"

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>

#include "rcutils/allocator.h"

// Include directives for member types
// Member `mode`
#include "rosidl_runtime_c/string_functions.h"

bool
rover_control_msgs__srv__SetOperationalMode_Request__init(rover_control_msgs__srv__SetOperationalMode_Request * msg)
{
  if (!msg) {
    return false;
  }
  // mode
  if (!rosidl_runtime_c__String__init(&msg->mode)) {
    rover_control_msgs__srv__SetOperationalMode_Request__fini(msg);
    return false;
  }
  return true;
}

void
rover_control_msgs__srv__SetOperationalMode_Request__fini(rover_control_msgs__srv__SetOperationalMode_Request * msg)
{
  if (!msg) {
    return;
  }
  // mode
  rosidl_runtime_c__String__fini(&msg->mode);
}

bool
rover_control_msgs__srv__SetOperationalMode_Request__are_equal(const rover_control_msgs__srv__SetOperationalMode_Request * lhs, const rover_control_msgs__srv__SetOperationalMode_Request * rhs)
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
rover_control_msgs__srv__SetOperationalMode_Request__copy(
  const rover_control_msgs__srv__SetOperationalMode_Request * input,
  rover_control_msgs__srv__SetOperationalMode_Request * output)
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

rover_control_msgs__srv__SetOperationalMode_Request *
rover_control_msgs__srv__SetOperationalMode_Request__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__srv__SetOperationalMode_Request * msg = (rover_control_msgs__srv__SetOperationalMode_Request *)allocator.allocate(sizeof(rover_control_msgs__srv__SetOperationalMode_Request), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rover_control_msgs__srv__SetOperationalMode_Request));
  bool success = rover_control_msgs__srv__SetOperationalMode_Request__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rover_control_msgs__srv__SetOperationalMode_Request__destroy(rover_control_msgs__srv__SetOperationalMode_Request * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rover_control_msgs__srv__SetOperationalMode_Request__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__init(rover_control_msgs__srv__SetOperationalMode_Request__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__srv__SetOperationalMode_Request * data = NULL;

  if (size) {
    data = (rover_control_msgs__srv__SetOperationalMode_Request *)allocator.zero_allocate(size, sizeof(rover_control_msgs__srv__SetOperationalMode_Request), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rover_control_msgs__srv__SetOperationalMode_Request__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rover_control_msgs__srv__SetOperationalMode_Request__fini(&data[i - 1]);
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
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__fini(rover_control_msgs__srv__SetOperationalMode_Request__Sequence * array)
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
      rover_control_msgs__srv__SetOperationalMode_Request__fini(&array->data[i]);
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

rover_control_msgs__srv__SetOperationalMode_Request__Sequence *
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__srv__SetOperationalMode_Request__Sequence * array = (rover_control_msgs__srv__SetOperationalMode_Request__Sequence *)allocator.allocate(sizeof(rover_control_msgs__srv__SetOperationalMode_Request__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rover_control_msgs__srv__SetOperationalMode_Request__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__destroy(rover_control_msgs__srv__SetOperationalMode_Request__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rover_control_msgs__srv__SetOperationalMode_Request__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__are_equal(const rover_control_msgs__srv__SetOperationalMode_Request__Sequence * lhs, const rover_control_msgs__srv__SetOperationalMode_Request__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rover_control_msgs__srv__SetOperationalMode_Request__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__copy(
  const rover_control_msgs__srv__SetOperationalMode_Request__Sequence * input,
  rover_control_msgs__srv__SetOperationalMode_Request__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rover_control_msgs__srv__SetOperationalMode_Request);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rover_control_msgs__srv__SetOperationalMode_Request * data =
      (rover_control_msgs__srv__SetOperationalMode_Request *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rover_control_msgs__srv__SetOperationalMode_Request__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rover_control_msgs__srv__SetOperationalMode_Request__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rover_control_msgs__srv__SetOperationalMode_Request__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}


// Include directives for member types
// Member `message`
// already included above
// #include "rosidl_runtime_c/string_functions.h"

bool
rover_control_msgs__srv__SetOperationalMode_Response__init(rover_control_msgs__srv__SetOperationalMode_Response * msg)
{
  if (!msg) {
    return false;
  }
  // success
  // message
  if (!rosidl_runtime_c__String__init(&msg->message)) {
    rover_control_msgs__srv__SetOperationalMode_Response__fini(msg);
    return false;
  }
  return true;
}

void
rover_control_msgs__srv__SetOperationalMode_Response__fini(rover_control_msgs__srv__SetOperationalMode_Response * msg)
{
  if (!msg) {
    return;
  }
  // success
  // message
  rosidl_runtime_c__String__fini(&msg->message);
}

bool
rover_control_msgs__srv__SetOperationalMode_Response__are_equal(const rover_control_msgs__srv__SetOperationalMode_Response * lhs, const rover_control_msgs__srv__SetOperationalMode_Response * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  // success
  if (lhs->success != rhs->success) {
    return false;
  }
  // message
  if (!rosidl_runtime_c__String__are_equal(
      &(lhs->message), &(rhs->message)))
  {
    return false;
  }
  return true;
}

bool
rover_control_msgs__srv__SetOperationalMode_Response__copy(
  const rover_control_msgs__srv__SetOperationalMode_Response * input,
  rover_control_msgs__srv__SetOperationalMode_Response * output)
{
  if (!input || !output) {
    return false;
  }
  // success
  output->success = input->success;
  // message
  if (!rosidl_runtime_c__String__copy(
      &(input->message), &(output->message)))
  {
    return false;
  }
  return true;
}

rover_control_msgs__srv__SetOperationalMode_Response *
rover_control_msgs__srv__SetOperationalMode_Response__create()
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__srv__SetOperationalMode_Response * msg = (rover_control_msgs__srv__SetOperationalMode_Response *)allocator.allocate(sizeof(rover_control_msgs__srv__SetOperationalMode_Response), allocator.state);
  if (!msg) {
    return NULL;
  }
  memset(msg, 0, sizeof(rover_control_msgs__srv__SetOperationalMode_Response));
  bool success = rover_control_msgs__srv__SetOperationalMode_Response__init(msg);
  if (!success) {
    allocator.deallocate(msg, allocator.state);
    return NULL;
  }
  return msg;
}

void
rover_control_msgs__srv__SetOperationalMode_Response__destroy(rover_control_msgs__srv__SetOperationalMode_Response * msg)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (msg) {
    rover_control_msgs__srv__SetOperationalMode_Response__fini(msg);
  }
  allocator.deallocate(msg, allocator.state);
}


bool
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__init(rover_control_msgs__srv__SetOperationalMode_Response__Sequence * array, size_t size)
{
  if (!array) {
    return false;
  }
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__srv__SetOperationalMode_Response * data = NULL;

  if (size) {
    data = (rover_control_msgs__srv__SetOperationalMode_Response *)allocator.zero_allocate(size, sizeof(rover_control_msgs__srv__SetOperationalMode_Response), allocator.state);
    if (!data) {
      return false;
    }
    // initialize all array elements
    size_t i;
    for (i = 0; i < size; ++i) {
      bool success = rover_control_msgs__srv__SetOperationalMode_Response__init(&data[i]);
      if (!success) {
        break;
      }
    }
    if (i < size) {
      // if initialization failed finalize the already initialized array elements
      for (; i > 0; --i) {
        rover_control_msgs__srv__SetOperationalMode_Response__fini(&data[i - 1]);
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
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__fini(rover_control_msgs__srv__SetOperationalMode_Response__Sequence * array)
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
      rover_control_msgs__srv__SetOperationalMode_Response__fini(&array->data[i]);
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

rover_control_msgs__srv__SetOperationalMode_Response__Sequence *
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__create(size_t size)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  rover_control_msgs__srv__SetOperationalMode_Response__Sequence * array = (rover_control_msgs__srv__SetOperationalMode_Response__Sequence *)allocator.allocate(sizeof(rover_control_msgs__srv__SetOperationalMode_Response__Sequence), allocator.state);
  if (!array) {
    return NULL;
  }
  bool success = rover_control_msgs__srv__SetOperationalMode_Response__Sequence__init(array, size);
  if (!success) {
    allocator.deallocate(array, allocator.state);
    return NULL;
  }
  return array;
}

void
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__destroy(rover_control_msgs__srv__SetOperationalMode_Response__Sequence * array)
{
  rcutils_allocator_t allocator = rcutils_get_default_allocator();
  if (array) {
    rover_control_msgs__srv__SetOperationalMode_Response__Sequence__fini(array);
  }
  allocator.deallocate(array, allocator.state);
}

bool
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__are_equal(const rover_control_msgs__srv__SetOperationalMode_Response__Sequence * lhs, const rover_control_msgs__srv__SetOperationalMode_Response__Sequence * rhs)
{
  if (!lhs || !rhs) {
    return false;
  }
  if (lhs->size != rhs->size) {
    return false;
  }
  for (size_t i = 0; i < lhs->size; ++i) {
    if (!rover_control_msgs__srv__SetOperationalMode_Response__are_equal(&(lhs->data[i]), &(rhs->data[i]))) {
      return false;
    }
  }
  return true;
}

bool
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__copy(
  const rover_control_msgs__srv__SetOperationalMode_Response__Sequence * input,
  rover_control_msgs__srv__SetOperationalMode_Response__Sequence * output)
{
  if (!input || !output) {
    return false;
  }
  if (output->capacity < input->size) {
    const size_t allocation_size =
      input->size * sizeof(rover_control_msgs__srv__SetOperationalMode_Response);
    rcutils_allocator_t allocator = rcutils_get_default_allocator();
    rover_control_msgs__srv__SetOperationalMode_Response * data =
      (rover_control_msgs__srv__SetOperationalMode_Response *)allocator.reallocate(
      output->data, allocation_size, allocator.state);
    if (!data) {
      return false;
    }
    // If reallocation succeeded, memory may or may not have been moved
    // to fulfill the allocation request, invalidating output->data.
    output->data = data;
    for (size_t i = output->capacity; i < input->size; ++i) {
      if (!rover_control_msgs__srv__SetOperationalMode_Response__init(&output->data[i])) {
        // If initialization of any new item fails, roll back
        // all previously initialized items. Existing items
        // in output are to be left unmodified.
        for (; i-- > output->capacity; ) {
          rover_control_msgs__srv__SetOperationalMode_Response__fini(&output->data[i]);
        }
        return false;
      }
    }
    output->capacity = input->size;
  }
  output->size = input->size;
  for (size_t i = 0; i < input->size; ++i) {
    if (!rover_control_msgs__srv__SetOperationalMode_Response__copy(
        &(input->data[i]), &(output->data[i])))
    {
      return false;
    }
  }
  return true;
}
