// generated from rosidl_generator_cpp/resource/idl__traits.hpp.em
// with input from rover_perception_msgs:msg/LedDetection.idl
// generated code does not contain a copyright notice

#ifndef ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__TRAITS_HPP_
#define ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__TRAITS_HPP_

#include <stdint.h>

#include <sstream>
#include <string>
#include <type_traits>

#include "rover_perception_msgs/msg/detail/led_detection__struct.hpp"
#include "rosidl_runtime_cpp/traits.hpp"

// Include directives for member types
// Member 'bearing'
#include "geometry_msgs/msg/detail/vector3__traits.hpp"

namespace rover_perception_msgs
{

namespace msg
{

inline void to_flow_style_yaml(
  const LedDetection & msg,
  std::ostream & out)
{
  out << "{";
  // member: pixel_u
  {
    out << "pixel_u: ";
    rosidl_generator_traits::value_to_yaml(msg.pixel_u, out);
    out << ", ";
  }

  // member: pixel_v
  {
    out << "pixel_v: ";
    rosidl_generator_traits::value_to_yaml(msg.pixel_v, out);
    out << ", ";
  }

  // member: area_px
  {
    out << "area_px: ";
    rosidl_generator_traits::value_to_yaml(msg.area_px, out);
    out << ", ";
  }

  // member: color_r
  {
    out << "color_r: ";
    rosidl_generator_traits::value_to_yaml(msg.color_r, out);
    out << ", ";
  }

  // member: color_g
  {
    out << "color_g: ";
    rosidl_generator_traits::value_to_yaml(msg.color_g, out);
    out << ", ";
  }

  // member: color_b
  {
    out << "color_b: ";
    rosidl_generator_traits::value_to_yaml(msg.color_b, out);
    out << ", ";
  }

  // member: bearing
  {
    out << "bearing: ";
    to_flow_style_yaml(msg.bearing, out);
  }
  out << "}";
}  // NOLINT(readability/fn_size)

inline void to_block_style_yaml(
  const LedDetection & msg,
  std::ostream & out, size_t indentation = 0)
{
  // member: pixel_u
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pixel_u: ";
    rosidl_generator_traits::value_to_yaml(msg.pixel_u, out);
    out << "\n";
  }

  // member: pixel_v
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "pixel_v: ";
    rosidl_generator_traits::value_to_yaml(msg.pixel_v, out);
    out << "\n";
  }

  // member: area_px
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "area_px: ";
    rosidl_generator_traits::value_to_yaml(msg.area_px, out);
    out << "\n";
  }

  // member: color_r
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "color_r: ";
    rosidl_generator_traits::value_to_yaml(msg.color_r, out);
    out << "\n";
  }

  // member: color_g
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "color_g: ";
    rosidl_generator_traits::value_to_yaml(msg.color_g, out);
    out << "\n";
  }

  // member: color_b
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "color_b: ";
    rosidl_generator_traits::value_to_yaml(msg.color_b, out);
    out << "\n";
  }

  // member: bearing
  {
    if (indentation > 0) {
      out << std::string(indentation, ' ');
    }
    out << "bearing:\n";
    to_block_style_yaml(msg.bearing, out, indentation + 2);
  }
}  // NOLINT(readability/fn_size)

inline std::string to_yaml(const LedDetection & msg, bool use_flow_style = false)
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

}  // namespace rover_perception_msgs

namespace rosidl_generator_traits
{

[[deprecated("use rover_perception_msgs::msg::to_block_style_yaml() instead")]]
inline void to_yaml(
  const rover_perception_msgs::msg::LedDetection & msg,
  std::ostream & out, size_t indentation = 0)
{
  rover_perception_msgs::msg::to_block_style_yaml(msg, out, indentation);
}

[[deprecated("use rover_perception_msgs::msg::to_yaml() instead")]]
inline std::string to_yaml(const rover_perception_msgs::msg::LedDetection & msg)
{
  return rover_perception_msgs::msg::to_yaml(msg);
}

template<>
inline const char * data_type<rover_perception_msgs::msg::LedDetection>()
{
  return "rover_perception_msgs::msg::LedDetection";
}

template<>
inline const char * name<rover_perception_msgs::msg::LedDetection>()
{
  return "rover_perception_msgs/msg/LedDetection";
}

template<>
struct has_fixed_size<rover_perception_msgs::msg::LedDetection>
  : std::integral_constant<bool, has_fixed_size<geometry_msgs::msg::Vector3>::value> {};

template<>
struct has_bounded_size<rover_perception_msgs::msg::LedDetection>
  : std::integral_constant<bool, has_bounded_size<geometry_msgs::msg::Vector3>::value> {};

template<>
struct is_message<rover_perception_msgs::msg::LedDetection>
  : std::true_type {};

}  // namespace rosidl_generator_traits

#endif  // ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__TRAITS_HPP_
