// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rover_control_msgs:msg/OperationalModeStatus.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__TRAITS_HPP_
#define ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "rover_control_msgs/msg/detail/operational_mode_status__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace rover_control_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const OperationalModeStatus & msg,
  std::ostream & out)
{
  out << "{";
  // member: stereo_cam
  {
    out << "stereo_cam: ";
    rosidl_generator_traits::value_to_yaml(msg.stereo_cam, out);
    out << ", ";
  }

  // member: mono_cam
  {
    out << "mono_cam: ";
    rosidl_generator_traits::value_to_yaml(msg.mono_cam, out);
    out << ", ";
  }

  // member: lidar
  {
    out << "lidar: ";
    rosidl_generator_traits::value_to_yaml(msg.lidar, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const OperationalModeStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: stereo_cam
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "stereo_cam: ";
    rosidl_generator_traits::value_to_yaml(msg.stereo_cam, out);
    out << "\n";
  }

  // member: mono_cam
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mono_cam: ";
    rosidl_generator_traits::value_to_yaml(msg.mono_cam, out);
    out << "\n";
  }

  // member: lidar
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "lidar: ";
    rosidl_generator_traits::value_to_yaml(msg.lidar, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const OperationalModeStatus & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace msg

}  // namespace rover_control_msgs

namespace rosidl_generator_traits
{

[[deprecated("use rover_control_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const rover_control_msgs::msg::OperationalModeStatus & msg,
  std::ostream & out, size_t indentation = 0)
{
  rover_control_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rover_control_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const rover_control_msgs::msg::OperationalModeStatus & msg)
{
  return rover_control_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<rover_control_msgs::msg::OperationalModeStatus>()
{
  return "rover_control_msgs::msg::OperationalModeStatus";
}

template<>
inline const char * name<rover_control_msgs::msg::OperationalModeStatus>()
{
  return "rover_control_msgs/msg/OperationalModeStatus";
}

template<>
struct has_fixed_size<rover_control_msgs::msg::OperationalModeStatus>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rover_control_msgs::msg::OperationalModeStatus>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rover_control_msgs::msg::OperationalModeStatus>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__TRAITS_HPP_
