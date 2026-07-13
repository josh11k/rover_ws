// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rover_control_msgs:msg/CurrentOperationalMode.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__MSG__DETAIL__CURRENT_OPERATIONAL_MODE__STRUCT_H_
#define ROVER_CONTROL_MSGS__MSG__DETAIL__CURRENT_OPERATIONAL_MODE__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'mode'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/CurrentOperationalMode in the package rover_control_msgs.
typedef struct rover_control_msgs__msg__CurrentOperationalMode
{
  rosidl_runtime_c__String mode;
} rover_control_msgs__msg__CurrentOperationalMode;

// Struct for a sequence of rover_control_msgs__msg__CurrentOperationalMode.
typedef struct rover_control_msgs__msg__CurrentOperationalMode__Sequence
{
  rover_control_msgs__msg__CurrentOperationalMode * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rover_control_msgs__msg__CurrentOperationalMode__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROVER_CONTROL_MSGS__MSG__DETAIL__CURRENT_OPERATIONAL_MODE__STRUCT_H_
