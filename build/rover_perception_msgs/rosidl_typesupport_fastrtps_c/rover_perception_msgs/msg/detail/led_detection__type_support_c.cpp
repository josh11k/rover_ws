// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from rover_perception_msgs:msg/LedDetection.idl
// generated code does not contain a copyright notice
#include "rover_perception_msgs/msg/detail/led_detection__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rover_perception_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "rover_perception_msgs/msg/detail/led_detection__struct.h"
#include "rover_perception_msgs/msg/detail/led_detection__functions.h"
#include "fastcdr/Cdr.h"

#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-parameter"
# ifdef __clang__
#  pragma clang diagnostic ignored "-Wdeprecated-register"
#  pragma clang diagnostic ignored "-Wreturn-type-c-linkage"
# endif
#endif
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif

// includes and forward declarations of message dependencies and their conversion functions

#if defined(__cplusplus)
extern "C"
{
#endif

#include "geometry_msgs/msg/detail/vector3__functions.h"  // bearing

// forward declare type support functions
ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_rover_perception_msgs
size_t get_serialized_size_geometry_msgs__msg__Vector3(
  const void * untyped_ros_message,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_rover_perception_msgs
size_t max_serialized_size_geometry_msgs__msg__Vector3(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment);

ROSIDL_TYPESUPPORT_FASTRTPS_C_IMPORT_rover_perception_msgs
const rosidl_message_type_support_t *
  ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, geometry_msgs, msg, Vector3)();


using _LedDetection__ros_msg_type = rover_perception_msgs__msg__LedDetection;

static bool _LedDetection__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _LedDetection__ros_msg_type * ros_message = static_cast<const _LedDetection__ros_msg_type *>(untyped_ros_message);
  // Field name: pixel_u
  {
    cdr << ros_message->pixel_u;
  }

  // Field name: pixel_v
  {
    cdr << ros_message->pixel_v;
  }

  // Field name: area_px
  {
    cdr << ros_message->area_px;
  }

  // Field name: color_r
  {
    cdr << ros_message->color_r;
  }

  // Field name: color_g
  {
    cdr << ros_message->color_g;
  }

  // Field name: color_b
  {
    cdr << ros_message->color_b;
  }

  // Field name: bearing
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, geometry_msgs, msg, Vector3
      )()->data);
    if (!callbacks->cdr_serialize(
        &ros_message->bearing, cdr))
    {
      return false;
    }
  }

  return true;
}

static bool _LedDetection__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _LedDetection__ros_msg_type * ros_message = static_cast<_LedDetection__ros_msg_type *>(untyped_ros_message);
  // Field name: pixel_u
  {
    cdr >> ros_message->pixel_u;
  }

  // Field name: pixel_v
  {
    cdr >> ros_message->pixel_v;
  }

  // Field name: area_px
  {
    cdr >> ros_message->area_px;
  }

  // Field name: color_r
  {
    cdr >> ros_message->color_r;
  }

  // Field name: color_g
  {
    cdr >> ros_message->color_g;
  }

  // Field name: color_b
  {
    cdr >> ros_message->color_b;
  }

  // Field name: bearing
  {
    const message_type_support_callbacks_t * callbacks =
      static_cast<const message_type_support_callbacks_t *>(
      ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(
        rosidl_typesupport_fastrtps_c, geometry_msgs, msg, Vector3
      )()->data);
    if (!callbacks->cdr_deserialize(
        cdr, &ros_message->bearing))
    {
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rover_perception_msgs
size_t get_serialized_size_rover_perception_msgs__msg__LedDetection(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _LedDetection__ros_msg_type * ros_message = static_cast<const _LedDetection__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name pixel_u
  {
    size_t item_size = sizeof(ros_message->pixel_u);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name pixel_v
  {
    size_t item_size = sizeof(ros_message->pixel_v);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name area_px
  {
    size_t item_size = sizeof(ros_message->area_px);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name color_r
  {
    size_t item_size = sizeof(ros_message->color_r);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name color_g
  {
    size_t item_size = sizeof(ros_message->color_g);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name color_b
  {
    size_t item_size = sizeof(ros_message->color_b);
    current_alignment += item_size +
      eprosima::fastcdr::Cdr::alignment(current_alignment, item_size);
  }
  // field.name bearing

  current_alignment += get_serialized_size_geometry_msgs__msg__Vector3(
    &(ros_message->bearing), current_alignment);

  return current_alignment - initial_alignment;
}

static uint32_t _LedDetection__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_rover_perception_msgs__msg__LedDetection(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rover_perception_msgs
size_t max_serialized_size_rover_perception_msgs__msg__LedDetection(
  bool & full_bounded,
  bool & is_plain,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  size_t last_member_size = 0;
  (void)last_member_size;
  (void)padding;
  (void)wchar_size;

  full_bounded = true;
  is_plain = true;

  // member: pixel_u
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: pixel_v
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: area_px
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint32_t);
    current_alignment += array_size * sizeof(uint32_t) +
      eprosima::fastcdr::Cdr::alignment(current_alignment, sizeof(uint32_t));
  }
  // member: color_r
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: color_g
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: color_b
  {
    size_t array_size = 1;

    last_member_size = array_size * sizeof(uint8_t);
    current_alignment += array_size * sizeof(uint8_t);
  }
  // member: bearing
  {
    size_t array_size = 1;


    last_member_size = 0;
    for (size_t index = 0; index < array_size; ++index) {
      bool inner_full_bounded;
      bool inner_is_plain;
      size_t inner_size;
      inner_size =
        max_serialized_size_geometry_msgs__msg__Vector3(
        inner_full_bounded, inner_is_plain, current_alignment);
      last_member_size += inner_size;
      current_alignment += inner_size;
      full_bounded &= inner_full_bounded;
      is_plain &= inner_is_plain;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = rover_perception_msgs__msg__LedDetection;
    is_plain =
      (
      offsetof(DataType, bearing) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _LedDetection__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_rover_perception_msgs__msg__LedDetection(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_LedDetection = {
  "rover_perception_msgs::msg",
  "LedDetection",
  _LedDetection__cdr_serialize,
  _LedDetection__cdr_deserialize,
  _LedDetection__get_serialized_size,
  _LedDetection__max_serialized_size
};

static rosidl_message_type_support_t _LedDetection__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_LedDetection,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rover_perception_msgs, msg, LedDetection)() {
  return &_LedDetection__type_support;
}

#if defined(__cplusplus)
}
#endif
