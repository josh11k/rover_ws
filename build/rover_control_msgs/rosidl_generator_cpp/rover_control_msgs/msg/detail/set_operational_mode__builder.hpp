// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rover_control_msgs:msg/SetOperationalMode.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__MSG__DETAIL__SET_OPERATIONAL_MODE__BUILDER_HPP_
#define ROVER_CONTROL_MSGS__MSG__DETAIL__SET_OPERATIONAL_MODE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rover_control_msgs/msg/detail/set_operational_mode__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rover_control_msgs
{

namespace msg
{

namespace builder
{

class Init_SetOperationalMode_mode
{
public:
  Init_SetOperationalMode_mode()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::rover_control_msgs::msg::SetOperationalMode mode(::rover_control_msgs::msg::SetOperationalMode::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rover_control_msgs::msg::SetOperationalMode msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::rover_control_msgs::msg::SetOperationalMode>()
{
  return rover_control_msgs::msg::builder::Init_SetOperationalMode_mode();
}

}  // namespace rover_control_msgs

#endif  // ROVER_CONTROL_MSGS__MSG__DETAIL__SET_OPERATIONAL_MODE__BUILDER_HPP_
