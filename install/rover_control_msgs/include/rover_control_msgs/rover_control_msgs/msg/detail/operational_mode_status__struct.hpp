// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rover_control_msgs:msg/OperationalModeStatus.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__STRUCT_HPP_
#define ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__rover_control_msgs__msg__OperationalModeStatus __attribute__((deprecated))
#else
# define DEPRECATED__rover_control_msgs__msg__OperationalModeStatus __declspec(deprecated)
#endif

namespace rover_control_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct OperationalModeStatus_
{
  using Type = OperationalModeStatus_<ContainerAllocator>;

  explicit OperationalModeStatus_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->stereo_cam = "";
      this->mono_cam = "";
      this->lidar = "";
    }
  }

  explicit OperationalModeStatus_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : stereo_cam(_alloc),
    mono_cam(_alloc),
    lidar(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->stereo_cam = "";
      this->mono_cam = "";
      this->lidar = "";
    }
  }

  // field types and members
  using _stereo_cam_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _stereo_cam_type stereo_cam;
  using _mono_cam_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _mono_cam_type mono_cam;
  using _lidar_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _lidar_type lidar;

  // setters for named parameter idiom
  Type & set__stereo_cam(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->stereo_cam = _arg;
    return *this;
  }
  Type & set__mono_cam(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->mono_cam = _arg;
    return *this;
  }
  Type & set__lidar(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->lidar = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator> *;
  using ConstRawPtr =
    const rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rover_control_msgs__msg__OperationalModeStatus
    std::shared_ptr<rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rover_control_msgs__msg__OperationalModeStatus
    std::shared_ptr<rover_control_msgs::msg::OperationalModeStatus_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const OperationalModeStatus_ & other) const
  {
    if (this->stereo_cam != other.stereo_cam) {
      return false;
    }
    if (this->mono_cam != other.mono_cam) {
      return false;
    }
    if (this->lidar != other.lidar) {
      return false;
    }
    return true;
  }
  bool operator!=(const OperationalModeStatus_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct OperationalModeStatus_

// alias to use template instance with default allocator
using OperationalModeStatus =
  rover_control_msgs::msg::OperationalModeStatus_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace rover_control_msgs

#endif  // ROVER_CONTROL_MSGS__MSG__DETAIL__OPERATIONAL_MODE_STATUS__STRUCT_HPP_
