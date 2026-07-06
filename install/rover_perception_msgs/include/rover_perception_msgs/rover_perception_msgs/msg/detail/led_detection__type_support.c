// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from rover_perception_msgs:msg/LedDetection.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "rover_perception_msgs/msg/detail/led_detection__rosidl_typesupport_introspection_c.h"
#include "rover_perception_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "rover_perception_msgs/msg/detail/led_detection__functions.h"
#include "rover_perception_msgs/msg/detail/led_detection__struct.h"


// Include directives for member types
// Member `bearing`
#include "geometry_msgs/msg/vector3.h"
// Member `bearing`
#include "geometry_msgs/msg/detail/vector3__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  rover_perception_msgs__msg__LedDetection__init(message_memory);
}

void rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_fini_function(void * message_memory)
{
  rover_perception_msgs__msg__LedDetection__fini(message_memory);
}

static rosidl_typesupport_introspection_c__MessageMember rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_message_member_array[7] = {
  {
    "pixel_u",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__LedDetection, pixel_u),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "pixel_v",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__LedDetection, pixel_v),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "area_px",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__LedDetection, area_px),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "color_r",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__LedDetection, color_r),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "color_g",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__LedDetection, color_g),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "color_b",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_UINT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__LedDetection, color_b),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "bearing",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__LedDetection, bearing),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_message_members = {
  "rover_perception_msgs__msg",  // message namespace
  "LedDetection",  // message name
  7,  // number of fields
  sizeof(rover_perception_msgs__msg__LedDetection),
  rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_message_member_array,  // message members
  rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_init_function,  // function to initialize message memory (memory has to be allocated)
  rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_message_type_support_handle = {
  0,
  &rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_rover_perception_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rover_perception_msgs, msg, LedDetection)() {
  rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_message_member_array[6].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, geometry_msgs, msg, Vector3)();
  if (!rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_message_type_support_handle.typesupport_identifier) {
    rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &rover_perception_msgs__msg__LedDetection__rosidl_typesupport_introspection_c__LedDetection_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
