// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rover_perception_msgs:msg/LedDetection.idl
// generated code does not contain a copyright notice

#ifndef ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__BUILDER_HPP_
#define ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rover_perception_msgs/msg/detail/led_detection__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rover_perception_msgs
{

namespace msg
{

namespace builder
{

class Init_LedDetection_bearing
{
public:
  explicit Init_LedDetection_bearing(::rover_perception_msgs::msg::LedDetection & msg)
  : msg_(msg)
  {}
  ::rover_perception_msgs::msg::LedDetection bearing(::rover_perception_msgs::msg::LedDetection::_bearing_type arg)
  {
    msg_.bearing = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rover_perception_msgs::msg::LedDetection msg_;
};

class Init_LedDetection_color_b
{
public:
  explicit Init_LedDetection_color_b(::rover_perception_msgs::msg::LedDetection & msg)
  : msg_(msg)
  {}
  Init_LedDetection_bearing color_b(::rover_perception_msgs::msg::LedDetection::_color_b_type arg)
  {
    msg_.color_b = std::move(arg);
    return Init_LedDetection_bearing(msg_);
  }

private:
  ::rover_perception_msgs::msg::LedDetection msg_;
};

class Init_LedDetection_color_g
{
public:
  explicit Init_LedDetection_color_g(::rover_perception_msgs::msg::LedDetection & msg)
  : msg_(msg)
  {}
  Init_LedDetection_color_b color_g(::rover_perception_msgs::msg::LedDetection::_color_g_type arg)
  {
    msg_.color_g = std::move(arg);
    return Init_LedDetection_color_b(msg_);
  }

private:
  ::rover_perception_msgs::msg::LedDetection msg_;
};

class Init_LedDetection_color_r
{
public:
  explicit Init_LedDetection_color_r(::rover_perception_msgs::msg::LedDetection & msg)
  : msg_(msg)
  {}
  Init_LedDetection_color_g color_r(::rover_perception_msgs::msg::LedDetection::_color_r_type arg)
  {
    msg_.color_r = std::move(arg);
    return Init_LedDetection_color_g(msg_);
  }

private:
  ::rover_perception_msgs::msg::LedDetection msg_;
};

class Init_LedDetection_area_px
{
public:
  explicit Init_LedDetection_area_px(::rover_perception_msgs::msg::LedDetection & msg)
  : msg_(msg)
  {}
  Init_LedDetection_color_r area_px(::rover_perception_msgs::msg::LedDetection::_area_px_type arg)
  {
    msg_.area_px = std::move(arg);
    return Init_LedDetection_color_r(msg_);
  }

private:
  ::rover_perception_msgs::msg::LedDetection msg_;
};

class Init_LedDetection_pixel_v
{
public:
  explicit Init_LedDetection_pixel_v(::rover_perception_msgs::msg::LedDetection & msg)
  : msg_(msg)
  {}
  Init_LedDetection_area_px pixel_v(::rover_perception_msgs::msg::LedDetection::_pixel_v_type arg)
  {
    msg_.pixel_v = std::move(arg);
    return Init_LedDetection_area_px(msg_);
  }

private:
  ::rover_perception_msgs::msg::LedDetection msg_;
};

class Init_LedDetection_pixel_u
{
public:
  Init_LedDetection_pixel_u()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_LedDetection_pixel_v pixel_u(::rover_perception_msgs::msg::LedDetection::_pixel_u_type arg)
  {
    msg_.pixel_u = std::move(arg);
    return Init_LedDetection_pixel_v(msg_);
  }

private:
  ::rover_perception_msgs::msg::LedDetection msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::rover_perception_msgs::msg::LedDetection>()
{
  return rover_perception_msgs::msg::builder::Init_LedDetection_pixel_u();
}

}  // namespace rover_perception_msgs

#endif  // ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__BUILDER_HPP_
