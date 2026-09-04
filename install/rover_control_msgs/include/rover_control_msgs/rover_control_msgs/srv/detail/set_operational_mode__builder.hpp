// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rover_control_msgs:srv/SetOperationalMode.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__BUILDER_HPP_
#define ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rover_control_msgs/srv/detail/set_operational_mode__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rover_control_msgs
{

namespace srv
{

namespace builder
{

class Init_SetOperationalMode_Request_mode
{
public:
  Init_SetOperationalMode_Request_mode()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  ::rover_control_msgs::srv::SetOperationalMode_Request mode(::rover_control_msgs::srv::SetOperationalMode_Request::_mode_type arg)
  {
    msg_.mode = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rover_control_msgs::srv::SetOperationalMode_Request msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::rover_control_msgs::srv::SetOperationalMode_Request>()
{
  return rover_control_msgs::srv::builder::Init_SetOperationalMode_Request_mode();
}

}  // namespace rover_control_msgs


namespace rover_control_msgs
{

namespace srv
{

namespace builder
{

class Init_SetOperationalMode_Response_message
{
public:
  explicit Init_SetOperationalMode_Response_message(::rover_control_msgs::srv::SetOperationalMode_Response & msg)
  : msg_(msg)
  {}
  ::rover_control_msgs::srv::SetOperationalMode_Response message(::rover_control_msgs::srv::SetOperationalMode_Response::_message_type arg)
  {
    msg_.message = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rover_control_msgs::srv::SetOperationalMode_Response msg_;
};

class Init_SetOperationalMode_Response_success
{
public:
  Init_SetOperationalMode_Response_success()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_SetOperationalMode_Response_message success(::rover_control_msgs::srv::SetOperationalMode_Response::_success_type arg)
  {
    msg_.success = std::move(arg);
    return Init_SetOperationalMode_Response_message(msg_);
  }

private:
  ::rover_control_msgs::srv::SetOperationalMode_Response msg_;
};

}  // namespace builder

}  // namespace srv

template<typename MessageType>
auto build();

template<>
inline
auto build<::rover_control_msgs::srv::SetOperationalMode_Response>()
{
  return rover_control_msgs::srv::builder::Init_SetOperationalMode_Response_success();
}

}  // namespace rover_control_msgs

#endif  // ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__BUILDER_HPP_
