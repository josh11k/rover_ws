// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rover_perception_msgs:msg/LedDetectionArray.idl
// generated code does not contain a copyright notice

#ifndef ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION_ARRAY__BUILDER_HPP_
#define ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION_ARRAY__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rover_perception_msgs/msg/detail/led_detection_array__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rover_perception_msgs
{

namespace msg
{

namespace builder
{

class Init_LedDetectionArray_detections
{
public:
  explicit Init_LedDetectionArray_detections(::rover_perception_msgs::msg::LedDetectionArray & msg)
  : msg_(msg)
  {}
  ::rover_perception_msgs::msg::LedDetectionArray detections(::rover_perception_msgs::msg::LedDetectionArray::_detections_type arg)
  {
    msg_.detections = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rover_perception_msgs::msg::LedDetectionArray msg_;
};

class Init_LedDetectionArray_header
{
public:
  Init_LedDetectionArray_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_LedDetectionArray_detections header(::rover_perception_msgs::msg::LedDetectionArray::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_LedDetectionArray_detections(msg_);
  }

private:
  ::rover_perception_msgs::msg::LedDetectionArray msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::rover_perception_msgs::msg::LedDetectionArray>()
{
  return rover_perception_msgs::msg::builder::Init_LedDetectionArray_header();
}

}  // namespace rover_perception_msgs

#endif  // ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION_ARRAY__BUILDER_HPP_
