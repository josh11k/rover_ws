// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rover_control_msgs:srv/SetOperationalMode.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__TRAITS_HPP_
#define ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "rover_control_msgs/srv/detail/set_operational_mode__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

namespace rover_control_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetOperationalMode_Request & msg,
  std::ostream & out)
{
  out << "{";
  // member: mode
  {
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SetOperationalMode_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: mode
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "mode: ";
    rosidl_generator_traits::value_to_yaml(msg.mode, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SetOperationalMode_Request & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace rover_control_msgs

namespace rosidl_generator_traits
{

[[deprecated("use rover_control_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const rover_control_msgs::srv::SetOperationalMode_Request & msg,
  std::ostream & out, size_t indentation = 0)
{
  rover_control_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rover_control_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const rover_control_msgs::srv::SetOperationalMode_Request & msg)
{
  return rover_control_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<rover_control_msgs::srv::SetOperationalMode_Request>()
{
  return "rover_control_msgs::srv::SetOperationalMode_Request";
}

template<>
inline const char * name<rover_control_msgs::srv::SetOperationalMode_Request>()
{
  return "rover_control_msgs/srv/SetOperationalMode_Request";
}

template<>
struct has_fixed_size<rover_control_msgs::srv::SetOperationalMode_Request>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rover_control_msgs::srv::SetOperationalMode_Request>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rover_control_msgs::srv::SetOperationalMode_Request>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rover_control_msgs
{

namespace srv
{

inline void to_flow_style_yaml(
  const SetOperationalMode_Response & msg,
  std::ostream & out)
{
  out << "{";
  // member: success
  {
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << ", ";
  }

  // member: message
  {
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const SetOperationalMode_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: success
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "success: ";
    rosidl_generator_traits::value_to_yaml(msg.success, out);
    out << "\n";
  }

  // member: message
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "message: ";
    rosidl_generator_traits::value_to_yaml(msg.message, out);
    out << "\n";
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const SetOperationalMode_Response & msg, bool use_flow_style = false)
{
  std::ostringstream out;
  if (use_flow_style) {
    to_flow_style_yaml(msg, out);
  } else {
    to_block_style_yaml(msg, out);
  }
  return out.str();
}

}  // namespace srv

}  // namespace rover_control_msgs

namespace rosidl_generator_traits
{

[[deprecated("use rover_control_msgs::srv::to_block_style_yaml() instead")]]
inline void to_yaml(
  const rover_control_msgs::srv::SetOperationalMode_Response & msg,
  std::ostream & out, size_t indentation = 0)
{
  rover_control_msgs::srv::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rover_control_msgs::srv::to_yaml() instead")]]
inline std::string to_yaml(const rover_control_msgs::srv::SetOperationalMode_Response & msg)
{
  return rover_control_msgs::srv::to_yaml(msg);
}

template<>
inline const char * data_type<rover_control_msgs::srv::SetOperationalMode_Response>()
{
  return "rover_control_msgs::srv::SetOperationalMode_Response";
}

template<>
inline const char * name<rover_control_msgs::srv::SetOperationalMode_Response>()
{
  return "rover_control_msgs/srv/SetOperationalMode_Response";
}

template<>
struct has_fixed_size<rover_control_msgs::srv::SetOperationalMode_Response>
  : std::integral_constant<bool, false> {};

template<>
struct has_bounded_size<rover_control_msgs::srv::SetOperationalMode_Response>
  : std::integral_constant<bool, false> {};

template<>
struct is_message<rover_control_msgs::srv::SetOperationalMode_Response>
  : std::true_type {};

}  // namespace rosidl_generator_traits

namespace rosidl_generator_traits
{

template<>
inline const char * data_type<rover_control_msgs::srv::SetOperationalMode>()
{
  return "rover_control_msgs::srv::SetOperationalMode";
}

template<>
inline const char * name<rover_control_msgs::srv::SetOperationalMode>()
{
  return "rover_control_msgs/srv/SetOperationalMode";
}

template<>
struct has_fixed_size<rover_control_msgs::srv::SetOperationalMode>
  : std::integral_constant<
    bool,
    has_fixed_size<rover_control_msgs::srv::SetOperationalMode_Request>::value &&
    has_fixed_size<rover_control_msgs::srv::SetOperationalMode_Response>::value
  >
{
};

template<>
struct has_bounded_size<rover_control_msgs::srv::SetOperationalMode>
  : std::integral_constant<
    bool,
    has_bounded_size<rover_control_msgs::srv::SetOperationalMode_Request>::value &&
    has_bounded_size<rover_control_msgs::srv::SetOperationalMode_Response>::value
  >
{
};

template<>
struct is_service<rover_control_msgs::srv::SetOperationalMode>
  : std::true_type
{
};

template<>
struct is_service_request<rover_control_msgs::srv::SetOperationalMode_Request>
  : std::true_type
{
};

template<>
struct is_service_response<rover_control_msgs::srv::SetOperationalMode_Response>
  : std::true_type
{
};

}  // namespace rosidl_generator_traits

#endif  // ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__TRAITS_HPP_
