// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from rover_control_msgs:msg/OperationalModeSettings.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "rover_control_msgs/msg/detail/operational_mode_settings__rosidl_typesupport_introspection_c.h"
#include "rover_control_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "rover_control_msgs/msg/detail/operational_mode_settings__functions.h"
#include "rover_control_msgs/msg/detail/operational_mode_settings__struct.h"


// Include directives for member types
// Member `stereo_cam`
// Member `mono_cam`
// Member `lidar`
#include "rosidl_runtime_c/string_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  rover_control_msgs__msg__OperationalModeSettings__init(message_memory);
}

void rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_fini_function(void * message_memory)
{
  rover_control_msgs__msg__OperationalModeSettings__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_message_member_array[3] = {
  {
    "stereo_cam",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_control_msgs__msg__OperationalModeSettings, stereo_cam),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "mono_cam",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_control_msgs__msg__OperationalModeSettings, mono_cam),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "lidar",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_control_msgs__msg__OperationalModeSettings, lidar),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_message_members = {
  "rover_control_msgs__msg",  // message namespace
  "OperationalModeSettings",  // message name
  3,  // number of fields
  sizeof(rover_control_msgs__msg__OperationalModeSettings),
  rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_message_member_array,  // message members
  rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_init_function,  // function to initialize message memory (memory has to be allocated)
  rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_message_type_support_handle = {
  0,
  &rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_rover_control_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rover_control_msgs, msg, OperationalModeSettings)() {
  if (!rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_message_type_support_handle.typesupport_identifier) {
    rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &rover_control_msgs__msg__OperationalModeSettings__rosidl_typesupport_introspection_c__OperationalModeSettings_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
