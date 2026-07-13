// generated from rosidl_typesupport_fastrtps_cpp/resource/idl__type_support.cpp.em
// with input from rover_control_msgs:msg/OperationalModeStatus.idl
// generated code does not contain a copyright notice
#include "rover_control_msgs/msg/detail/operational_mode_status__rosidl_typesupport_fastrtps_cpp.hpp"
#include "rover_control_msgs/msg/detail/operational_mode_status__struct.hpp"

#include <limits>
#include <stdexcept>
#include <string>
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_fastrtps_cpp/identifier.hpp"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support.h"
#include "rosidl_typesupport_fastrtps_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_fastrtps_cpp/wstring_conversion.hpp"
#include "fastcdr/Cdr.h"


// forward declaration of message dependencies and their conversion functions

namespace rover_control_msgs
{

namespace msg
{

namespace typesupport_fastrtps_cpp
{

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_rover_control_msgs
cdr_serialize(
  const rover_control_msgs::msg::OperationalModeStatus & ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  // Member: stereo_cam
  cdr << ros_message.stereo_cam;
  // Member: mono_cam
  cdr << ros_message.mono_cam;
  // Member: lidar
  cdr << ros_message.lidar;
  return true;
}

bool
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_rover_control_msgs
cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  rover_control_msgs::msg::OperationalModeStatus & ros_message)
{
  // Member: stereo_cam
  cdr >> ros_message.stereo_cam;

  // Member: mono_cam
  cdr >> ros_message.mono_cam;

  // Member: lidar
  cdr >> ros_message.lidar;

  return true;
}  // NOLINT(readability/fn_size)

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_rover_control_msgs
get_serialized_size(
  const rover_control_msgs::msg::OperationalModeStatus & ros_message,
  size_t current_alignment)
{
  size_t initial_alignment = current_alignment;

  const size_t padding = 4;
  const size_t wchar_size = 4;
  (void)padding;
  (void)wchar_size;

  // Member: stereo_cam
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.stereo_cam.size() + 1);
  // Member: mono_cam
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.mono_cam.size() + 1);
  // Member: lidar
  current_alignment += padding +
    eprosima::fastcdr::Cdr::alignment(current_alignment, padding) +
    (ros_message.lidar.size() + 1);

  return current_alignment - initial_alignment;
}

size_t
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_PUBLIC_rover_control_msgs
max_serialized_size_OperationalModeStatus(
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


  // Member: stereo_cam
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

  // Member: mono_cam
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

  // Member: lidar
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
    using DataType = rover_control_msgs::msg::OperationalModeStatus;
    is_plain =
      (
      offsetof(DataType, lidar) +
      last_member_size
      ) == ret_val;
  }

  return ret_val;
}

static bool _OperationalModeStatus__cdr_serialize(
  const void * untyped_ros_message,
  eprosima::fastcdr::Cdr & cdr)
{
  auto typed_message =
    static_cast<const rover_control_msgs::msg::OperationalModeStatus *>(
    untyped_ros_message);
  return cdr_serialize(*typed_message, cdr);
}

static bool _OperationalModeStatus__cdr_deserialize(
  eprosima::fastcdr::Cdr & cdr,
  void * untyped_ros_message)
{
  auto typed_message =
    static_cast<rover_control_msgs::msg::OperationalModeStatus *>(
    untyped_ros_message);
  return cdr_deserialize(cdr, *typed_message);
}

static uint32_t _OperationalModeStatus__get_serialized_size(
  const void * untyped_ros_message)
{
  auto typed_message =
    static_cast<const rover_control_msgs::msg::OperationalModeStatus *>(
    untyped_ros_message);
  return static_cast<uint32_t>(get_serialized_size(*typed_message, 0));
}

static size_t _OperationalModeStatus__max_serialized_size(char & bounds_info)
{
  bool full_bounded;
  bool is_plain;
  size_t ret_val;

  ret_val = max_serialized_size_OperationalModeStatus(full_bounded, is_plain, 0);

  bounds_info =
    is_plain ? ROSIDL_TYPESUPPORT_FASTRTPS_PLAIN_TYPE :
    full_bounded ? ROSIDL_TYPESUPPORT_FASTRTPS_BOUNDED_TYPE : ROSIDL_TYPESUPPORT_FASTRTPS_UNBOUNDED_TYPE;
  return ret_val;
}

static message_type_support_callbacks_t _OperationalModeStatus__callbacks = {
  "rover_control_msgs::msg",
  "OperationalModeStatus",
  _OperationalModeStatus__cdr_serialize,
  _OperationalModeStatus__cdr_deserialize,
  _OperationalModeStatus__get_serialized_size,
  _OperationalModeStatus__max_serialized_size
};

static rosidl_message_type_support_t _OperationalModeStatus__handle = {
  rosidl_typesupport_fastrtps_cpp::typesupport_identifier,
  &_OperationalModeStatus__callbacks,
  get_message_typesupport_handle_function,
};

}  // namespace typesupport_fastrtps_cpp

}  // namespace msg

}  // namespace rover_control_msgs

namespace rosidl_typesupport_fastrtps_cpp
{

template<>
ROSIDL_TYPESUPPORT_FASTRTPS_CPP_EXPORT_rover_control_msgs
const rosidl_message_type_support_t *
get_message_type_support_handle<rover_control_msgs::msg::OperationalModeStatus>()
{
  return &rover_control_msgs::msg::typesupport_fastrtps_cpp::_OperationalModeStatus__handle;
}

}  // namespace rosidl_typesupport_fastrtps_cpp

#ifdef __cplusplus
extern "C"
{
#endif

const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_fastrtps_cpp, rover_control_msgs, msg, OperationalModeStatus)() {
  return &rover_control_msgs::msg::typesupport_fastrtps_cpp::_OperationalModeStatus__handle;
}

#ifdef __cplusplus
}
#endif
