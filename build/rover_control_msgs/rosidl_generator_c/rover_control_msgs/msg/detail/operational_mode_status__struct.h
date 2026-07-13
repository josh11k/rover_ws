// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rover_control_msgs:msg/OperationalModeStatus.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__STRUCT_H_
#define ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'stereo_cam'
// Member 'mono_cam'
// Member 'lidar'
#include "rosidl_runtime_c/string.h"

/// Struct defined in msg/OperationalModeStatus in the package rover_control_msgs.
typedef struct rover_control_msgs__msg__OperationalModeStatus
{
  rosidl_runtime_c__String stereo_cam;
  rosidl_runtime_c__String mono_cam;
  rosidl_runtime_c__String lidar;
} rover_control_msgs__msg__OperationalModeStatus;

// Struct for a sequence of rover_control_msgs__msg__OperationalModeStatus.
typedef struct rover_control_msgs__msg__OperationalModeStatus__Sequence
{
  rover_control_msgs__msg__OperationalModeStatus * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rover_control_msgs__msg__OperationalModeStatus__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__STRUCT_H_
