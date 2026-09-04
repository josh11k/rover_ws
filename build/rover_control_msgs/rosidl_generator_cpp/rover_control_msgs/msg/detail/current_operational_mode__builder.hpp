// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rover_control_msgs:msg/CurrentOperationalMode.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__MSG__DETAIL__CURRENT_OPERATIONAL_MODE__BUILDER_HPP_
#define ROVER_CONTROL_MSGS__MSG__DETAIL__CURRENT_OPERATIONAL_MODE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rover_control_msgs/msg/detail/current_operational_mode__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rover_control_msgs
{

namespace msg
{

namespace builder
{

class Init_CurrentOperationalMode_mode
{
public:
  Init_CurrentOperationalMode_mode()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::rover_control_msgs::msg::CurrentOperationalMode mode(::rover_control_msgs::msg::CurrentOperationalMode::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rover_control_msgs::msg::CurrentOperationalMode msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::rover_control_msgs::msg::CurrentOperationalMode>()
{
  return rover_control_msgs::msg::builder::Init_CurrentOperationalMode_mode();
}

}  // namespace rover_control_msgs

#endif  // ROVER_CONTROL_MSGS__MSG__DETAIL__CURRENT_OPERATIONAL_MODE__BUILDER_HPP_
