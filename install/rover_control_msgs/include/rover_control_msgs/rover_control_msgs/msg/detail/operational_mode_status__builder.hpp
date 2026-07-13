// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rover_control_msgs:msg/OperationalModeStatus.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__BUILDER_HPP_
#define ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rover_control_msgs/msg/detail/operational_mode_status__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rover_control_msgs
{

namespace msg
{

namespace builder
{

class Init_OperationalModeStatus_lidar
{
public:
  explicit Init_OperationalModeStatus_lidar(::rover_control_msgs::msg::OperationalModeStatus & msg)
  : msg_(msg)
  {}
  ::rover_control_msgs::msg::OperationalModeStatus lidar(::rover_control_msgs::msg::OperationalModeStatus::_lidar_type arg)
  {
    msg_.lidar = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rover_control_msgs::msg::OperationalModeStatus msg_;
};

class Init_OperationalModeStatus_mono_cam
{
public:
  explicit Init_OperationalModeStatus_mono_cam(::rover_control_msgs::msg::OperationalModeStatus & msg)
  : msg_(msg)
  {}
  Init_OperationalModeStatus_lidar mono_cam(::rover_control_msgs::msg::OperationalModeStatus::_mono_cam_type arg)
  {
    msg_.mono_cam = std::move(arg);
    return Init_OperationalModeStatus_lidar(msg_);
  }

private:
  ::rover_control_msgs::msg::OperationalModeStatus msg_;
};

class Init_OperationalModeStatus_stereo_cam
{
public:
  Init_OperationalModeStatus_stereo_cam()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_OperationalModeStatus_mono_cam stereo_cam(::rover_control_msgs::msg::OperationalModeStatus::_stereo_cam_type arg)
  {
    msg_.stereo_cam = std::move(arg);
    return Init_OperationalModeStatus_mono_cam(msg_);
  }

private:
  ::rover_control_msgs::msg::OperationalModeStatus msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::rover_control_msgs::msg::OperationalModeStatus>()
{
  return rover_control_msgs::msg::builder::Init_OperationalModeStatus_stereo_cam();
}

}  // namespace rover_control_msgs

#endif  // ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__BUILDER_HPP_
