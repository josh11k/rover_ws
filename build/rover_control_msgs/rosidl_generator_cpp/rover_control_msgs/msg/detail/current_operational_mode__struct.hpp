// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rover_control_msgs:msg/CurrentOperationalMode.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__MSG__DETAIL__CURRENT_OPERATIONAL_MODE__STRUCT_HPP_
#define ROVER_CONTROL_MSGS__MSG__DETAIL__CURRENT_OPERATIONAL_MODE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__rover_control_msgs__msg__CurrentOperationalMode __attribute__((deprecated))
#else
# define DEPRECATED__rover_control_msgs__msg__CurrentOperationalMode __declspec(deprecated)
#endif

namespace rover_control_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct CurrentOperationalMode_
{
  using Type = CurrentOperationalMode_<ContainerAllocator>;

  explicit CurrentOperationalMode_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mode = "";
    }
  }

  explicit CurrentOperationalMode_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : mode(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mode = "";
    }
  }

  // field types and members
  using _mode_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _mode_type mode;

  // setters for named parameter idiom
  Type & set__mode(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->mode = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator> *;
  using ConstRawPtr =
    const rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rover_control_msgs__msg__CurrentOperationalMode
    std::shared_ptr<rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rover_control_msgs__msg__CurrentOperationalMode
    std::shared_ptr<rover_control_msgs::msg::CurrentOperationalMode_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const CurrentOperationalMode_ & other) const
  {
    if (this->mode != other.mode) {
      return false;
    }
    return true;
  }
  bool operator!=(const CurrentOperationalMode_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct CurrentOperationalMode_

// alias to use template instance with default allocator
using CurrentOperationalMode =
  rover_control_msgs::msg::CurrentOperationalMode_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace rover_control_msgs

#endif  // ROVER_CONTROL_MSGS__MSG__DETAIL__CURRENT_OPERATIONAL_MODE__STRUCT_HPP_
