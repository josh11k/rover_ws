// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from rover_control_msgs:msg/OperationalModeSettings.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "rover_control_msgs/msg/detail/operational_mode_settings__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace rover_control_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void OperationalModeSettings_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) rover_control_msgs::msg::OperationalModeSettings(_init);
}

void OperationalModeSettings_fini_function(void * message_memory)
{
  auto typed_message = static_cast<rover_control_msgs::msg::OperationalModeSettings *>(message_memory);
  typed_message->~OperationalModeSettings();
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember OperationalModeSettings_message_member_array[3] = {
  {
    "stereo_cam",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_control_msgs::msg::OperationalModeSettings, stereo_cam),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "mono_cam",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_control_msgs::msg::OperationalModeSettings, mono_cam),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "lidar",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_STRING,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_control_msgs::msg::OperationalModeSettings, lidar),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers OperationalModeSettings_message_members = {
  "rover_control_msgs::msg",  // message namespace
  "OperationalModeSettings",  // message name
  3,  // number of fields
  sizeof(rover_control_msgs::msg::OperationalModeSettings),
  OperationalModeSettings_message_member_array,  // message members
  OperationalModeSettings_init_function,  // function to initialize message memory (memory has to be allocated)
  OperationalModeSettings_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t OperationalModeSettings_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &OperationalModeSettings_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace rover_control_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<rover_control_msgs::msg::OperationalModeSettings>()
{
  return &::rover_control_msgs::msg::rosidl_typesupport_introspection_cpp::OperationalModeSettings_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, rover_control_msgs, msg, OperationalModeSettings)() {
  return &::rover_control_msgs::msg::rosidl_typesupport_introspection_cpp::OperationalModeSettings_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
