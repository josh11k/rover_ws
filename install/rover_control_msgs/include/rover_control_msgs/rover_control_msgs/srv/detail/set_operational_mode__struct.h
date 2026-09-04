// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rover_control_msgs:srv/SetOperationalMode.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__STRUCT_H_
#define ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__STRUCT_H_

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

/// Struct defined in srv/SetOperationalMode in the package rover_control_msgs.
typedef struct rover_control_msgs__srv__SetOperationalMode_Request
{
  rosidl_runtime_c__String mode;
} rover_control_msgs__srv__SetOperationalMode_Request;

// Struct for a sequence of rover_control_msgs__srv__SetOperationalMode_Request.
typedef struct rover_control_msgs__srv__SetOperationalMode_Request__Sequence
{
  rover_control_msgs__srv__SetOperationalMode_Request * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rover_control_msgs__srv__SetOperationalMode_Request__Sequence;


// Constants defined in the message

// Include directives for member types
// Member 'message'
// already included above
// #include "rosidl_runtime_c/string.h"

/// Struct defined in srv/SetOperationalMode in the package rover_control_msgs.
typedef struct rover_control_msgs__srv__SetOperationalMode_Response
{
  bool success;
  rosidl_runtime_c__String message;
} rover_control_msgs__srv__SetOperationalMode_Response;

// Struct for a sequence of rover_control_msgs__srv__SetOperationalMode_Response.
typedef struct rover_control_msgs__srv__SetOperationalMode_Response__Sequence
{
  rover_control_msgs__srv__SetOperationalMode_Response * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rover_control_msgs__srv__SetOperationalMode_Response__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__STRUCT_H_
