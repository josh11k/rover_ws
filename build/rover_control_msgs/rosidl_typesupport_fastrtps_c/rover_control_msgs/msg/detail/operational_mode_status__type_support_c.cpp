// generated from rosidl_typesupport_fastrtps_c/resource/idl__type_support_c.cpp.em
// with input from rover_control_msgs:msg/OperationalModeStatus.idl
// generated code does not contain a copyright notice
#include "rover_control_msgs/msg/detail/operational_mode_status__rosidl_typesupport_fastrtps_c.h"


#include <cassert>
#include <limits>
#include <string>
#include "rosidl_typesupport_fastrtps_c/identifier.h"
#include "rosidl_typesupport_fastrtps_c/wstring_conversion.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rover_control_msgs/msg/rosidl_typesupport_fastrtps_c__visibility_control.h"
#include "rover_control_msgs/msg/detail/operational_mode_status__struct.h"
#include "rover_control_msgs/msg/detail/operational_mode_status__functions.h"
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

#include "rosidl_runtime_c/string.h"  // lidar, mono_cam, stereo_cam
#include "rosidl_runtime_c/string_functions.h"  // lidar, mono_cam, stereo_cam

// forward declare type support functions


using _OperationalModeStatus__ros_msg_type = rover_control_msgs__msg__OperationalModeStatus;

static bool _OperationalModeStatus__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  const _OperationalModeStatus__ros_msg_type * ros_message = static_cast<const _OperationalModeStatus__ros_msg_type *>(untyped_ros_message);
  // Field name: stereo_cam
  {
    const rosidl_runtime_c__String * str = &ros_message->stereo_cam;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: mono_cam
  {
    const rosidl_runtime_c__String * str = &ros_message->mono_cam;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  // Field name: lidar
  {
    const rosidl_runtime_c__String * str = &ros_message->lidar;
    if (str->capacity == 0 || str->capacity <= str->size) {
      fprintf(stderr, "string capacity not greater than size\n");
      return false;
    }
    if (str->data[str->size] != '\0') {
      fprintf(stderr, "string not null-terminated\n");
      return false;
    }
    cdr << str->data;
  }

  return true;
}

static bool _OperationalModeStatus__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  if (!untyped_ros_message) {
    fprintf(stderr, "ros message handle is null\n");
    return false;
  }
  _OperationalModeStatus__ros_msg_type * ros_message = static_cast<_OperationalModeStatus__ros_msg_type *>(untyped_ros_message);
  // Field name: stereo_cam
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->stereo_cam.data) {
      rosidl_runtime_c__String__init(&ros_message->stereo_cam);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->stereo_cam,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'stereo_cam'\n");
      return false;
    }
  }

  // Field name: mono_cam
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->mono_cam.data) {
      rosidl_runtime_c__String__init(&ros_message->mono_cam);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->mono_cam,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'mono_cam'\n");
      return false;
    }
  }

  // Field name: lidar
  {
    std::string tmp;
    cdr >> tmp;
    if (!ros_message->lidar.data) {
      rosidl_runtime_c__String__init(&ros_message->lidar);
    }
    bool succeeded = rosidl_runtime_c__String__assign(
      &ros_message->lidar,
      tmp.c_str());
    if (!succeeded) {
      fprintf(stderr, "failed to assign string into field 'lidar'\n");
      return false;
    }
  }

  return true;
}  // NOLINT(readability/fn_size)

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rover_control_msgs
size_t get_serialized_size_rover_control_msgs__msg__OperationalModeStatus(
  const void * untyped_ros_message,
  size_t current_alignment)
{
  const _OperationalModeStatus__ros_msg_type * ros_message = static_cast<const _OperationalModeStatus__ros_msg_type *>(untyped_ros_message);
  (void)ros_message;
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // field.name stereo_cam
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->stereo_cam.size + 1);
  // field.name mono_cam
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->mono_cam.size + 1);
  // field.name lidar
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message->lidar.size + 1);

  return current_alignment - initial_alignment;
}

static uint32_t _OperationalModeStatus__get_serialized_size(const void * untyped_ros_message)
{
  return static_cast<uint32_t>(
    get_serialized_size_rover_control_msgs__msg__OperationalModeStatus(
      untyped_ros_message, 0));
}

ROSIDL_TYPESUPPORT_FASTRTPS_C_PUBLIC_rover_control_msgs
size_t max_serialized_size_rover_control_msgs__msg__OperationalModeStatus(
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

  // member: stereo_cam
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // member: mono_cam
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }
  // member: lidar
  {
    size_t array_size = 1;

    full_bounded = false;
    is_plain = false;
    for (size_t index = 0; index < array_size; ++index) {
      current_alignment += padding +
        eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
        1;
    }
  }

  size_t ret_val = current_alignment - initial_alignment;
  if (is_plain) {
    // All members are plain, and type is not empty.
    // We still need to check that the in-memory alignment
    // is the same as the CDR mandated alignment.
    using DataType = rover_control_msgs__msg__OperationalModeStatus;
    is_plain =
      (
      offsetof(DataType, lidar) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static size_t _OperationalModeStatus__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_rover_control_msgs__msg__OperationalModeStatus(
    full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}


static message_type_support_callbacks_t __callbacks_OperationalModeStatus = {
  "rover_control_msgs::msg",
  "OperationalModeStatus",
  _OperationalModeStatus__cdr_serialize,
  _OperationalModeStatus__cdr_deserialize,
  _OperationalModeStatus__get_serialized_size,
  _OperationalModeStatus__max_serialized_size
};

static rosidl_message_type_support_t _OperationalModeStatus__type_support = {
  rosidl_typesupport_fastrtps_c__identifier,
  &__callbacks_OperationalModeStatus,
  get_message_typesupport_handle_function,
};

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_c, rover_control_msgs, msg, OperationalModeStatus)() {
  return &_OperationalModeStatus__type_support;
}

#if defined(__cplusplus)
}
#endif
