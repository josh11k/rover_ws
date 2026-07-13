// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rover_control_msgs:srv/SetOperationalMode.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__STRUCT_HPP_
#define ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


#ifndef _WIN32
# define DEPRECATED__rover_control_msgs__srv__SetOperationalMode_Request __attribute__((deprecated))
#else
# define DEPRECATED__rover_control_msgs__srv__SetOperationalMode_Request __declspec(deprecated)
#endif

namespace rover_control_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SetOperationalMode_Request_
{
  using Type = SetOperationalMode_Request_<ContainerAllocator>;

  explicit SetOperationalMode_Request_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->mode = "";
    }
  }

  explicit SetOperationalMode_Request_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
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
    rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator> *;
  using ConstRawPtr =
    const rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rover_control_msgs__srv__SetOperationalMode_Request
    std::shared_ptr<rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rover_control_msgs__srv__SetOperationalMode_Request
    std::shared_ptr<rover_control_msgs::srv::SetOperationalMode_Request_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SetOperationalMode_Request_ & other) const
  {
    if (this->mode != other.mode) {
      return false;
    }
    return true;
  }
  bool operator!=(const SetOperationalMode_Request_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SetOperationalMode_Request_

// alias to use template instance with default allocator
using SetOperationalMode_Request =
  rover_control_msgs::srv::SetOperationalMode_Request_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace rover_control_msgs


#ifndef _WIN32
# define DEPRECATED__rover_control_msgs__srv__SetOperationalMode_Response __attribute__((deprecated))
#else
# define DEPRECATED__rover_control_msgs__srv__SetOperationalMode_Response __declspec(deprecated)
#endif

namespace rover_control_msgs
{

namespace srv
{

// message struct
template<class ContainerAllocator>
struct SetOperationalMode_Response_
{
  using Type = SetOperationalMode_Response_<ContainerAllocator>;

  explicit SetOperationalMode_Response_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  explicit SetOperationalMode_Response_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : message(_alloc)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->success = false;
      this->message = "";
    }
  }

  // field types and members
  using _success_type =
    bool;
  _success_type success;
  using _message_type =
    std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>>;
  _message_type message;

  // setters for named parameter idiom
  Type & set__success(
    const bool & _arg)
  {
    this->success = _arg;
    return *this;
  }
  Type & set__message(
    const std::basic_string<char, std::char_traits<char>, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<char>> & _arg)
  {
    this->message = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator> *;
  using ConstRawPtr =
    const rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rover_control_msgs__srv__SetOperationalMode_Response
    std::shared_ptr<rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rover_control_msgs__srv__SetOperationalMode_Response
    std::shared_ptr<rover_control_msgs::srv::SetOperationalMode_Response_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const SetOperationalMode_Response_ & other) const
  {
    if (this->success != other.success) {
      return false;
    }
    if (this->message != other.message) {
      return false;
    }
    return true;
  }
  bool operator!=(const SetOperationalMode_Response_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct SetOperationalMode_Response_

// alias to use template instance with default allocator
using SetOperationalMode_Response =
  rover_control_msgs::srv::SetOperationalMode_Response_<std::allocator<void>>;

// constant definitions

}  // namespace srv

}  // namespace rover_control_msgs

namespace rover_control_msgs
{

namespace srv
{

struct SetOperationalMode
{
  using Request = rover_control_msgs::srv::SetOperationalMode_Request;
  using Response = rover_control_msgs::srv::SetOperationalMode_Response;
};

}  // namespace srv

}  // namespace rover_control_msgs

#endif  // ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__STRUCT_HPP_
