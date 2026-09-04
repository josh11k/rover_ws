// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from rover_perception_msgs:msg/LedDetectionArray.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "rover_perception_msgs/msg/detail/led_detection_array__rosidl_typesupport_introspection_c.h"
#include "rover_perception_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "rover_perception_msgs/msg/detail/led_detection_array__functions.h"
#include "rover_perception_msgs/msg/detail/led_detection_array__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `detections`
#include "rover_perception_msgs/msg/led_detection.h"
// Member `detections`
#include "rover_perception_msgs/msg/detail/led_detection__rosidl_typesupport_introspection_c.h"

#ifdef __cplusplus
extern "C"
{
#endif

void rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  rover_perception_msgs__msg__LedDetectionArray__init(message_memory);
}

void rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_fini_function(void * message_memory)
{
  rover_perception_msgs__msg__LedDetectionArray__fini(message_memory);
}

size_t rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__size_function__LedDetectionArray__detections(
  const void * untyped_member)
{
  const rover_perception_msgs__msg__LedDetection__Sequence * member =
    (const rover_perception_msgs__msg__LedDetection__Sequence *)(untyped_member);
  return member->size;
}

const void * rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__get_const_function__LedDetectionArray__detections(
  const void * untyped_member, size_t index)
{
  const rover_perception_msgs__msg__LedDetection__Sequence * member =
    (const rover_perception_msgs__msg__LedDetection__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__get_function__LedDetectionArray__detections(
  void * untyped_member, size_t index)
{
  rover_perception_msgs__msg__LedDetection__Sequence * member =
    (rover_perception_msgs__msg__LedDetection__Sequence *)(untyped_member);
  return &member->data[index];
}

void rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__fetch_function__LedDetectionArray__detections(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const rover_perception_msgs__msg__LedDetection * item =
    ((const rover_perception_msgs__msg__LedDetection *)
    rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__get_const_function__LedDetectionArray__detections(untyped_member, index));
  rover_perception_msgs__msg__LedDetection * value =
    (rover_perception_msgs__msg__LedDetection *)(untyped_value);
  *value = *item;
}

void rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__assign_function__LedDetectionArray__detections(
  void * untyped_member, size_t index, const void * untyped_value)
{
  rover_perception_msgs__msg__LedDetection * item =
    ((rover_perception_msgs__msg__LedDetection *)
    rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__get_function__LedDetectionArray__detections(untyped_member, index));
  const rover_perception_msgs__msg__LedDetection * value =
    (const rover_perception_msgs__msg__LedDetection *)(untyped_value);
  *item = *value;
}

bool rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__resize_function__LedDetectionArray__detections(
  void * untyped_member, size_t size)
{
  rover_perception_msgs__msg__LedDetection__Sequence * member =
    (rover_perception_msgs__msg__LedDetection__Sequence *)(untyped_member);
  rover_perception_msgs__msg__LedDetection__Sequence__fini(member);
  return rover_perception_msgs__msg__LedDetection__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_message_member_array[2] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__LedDetectionArray, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "detections",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__LedDetectionArray, detections),  // bytes offset in struct
    NULL,  // default value
    rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__size_function__LedDetectionArray__detections,  // size() function pointer
    rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__get_const_function__LedDetectionArray__detections,  // get_const(index) function pointer
    rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__get_function__LedDetectionArray__detections,  // get(index) function pointer
    rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__fetch_function__LedDetectionArray__detections,  // fetch(index, &value) function pointer
    rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__assign_function__LedDetectionArray__detections,  // assign(index, value) function pointer
    rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__resize_function__LedDetectionArray__detections  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_message_members = {
  "rover_perception_msgs__msg",  // message namespace
  "LedDetectionArray",  // message name
  2,  // number of fields
  sizeof(rover_perception_msgs__msg__LedDetectionArray),
  rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_message_member_array,  // message members
  rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_init_function,  // function to initialize message memory (memory has to be allocated)
  rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_message_type_support_handle = {
  0,
  &rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_rover_perception_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rover_perception_msgs, msg, LedDetectionArray)() {
  rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rover_perception_msgs, msg, LedDetection)();
  if (!rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_message_type_support_handle.typesupport_identifier) {
    rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &rover_perception_msgs__msg__LedDetectionArray__rosidl_typesupport_introspection_c__LedDetectionArray_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
