// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rover_perception_msgs:msg/LedDetection.idl
// generated code does not contain a copyright notice

#ifndef ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__STRUCT_HPP_
#define ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'bearing'
#include "geometry_msgs/msg/detail/vector3__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__rover_perception_msgs__msg__LedDetection __attribute__((deprecated))
#else
# define DEPRECATED__rover_perception_msgs__msg__LedDetection __declspec(deprecated)
#endif

namespace rover_perception_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct LedDetection_
{
  using Type = LedDetection_<ContainerAllocator>;

  explicit LedDetection_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : bearing(_init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->pixel_u = 0.0f;
      this->pixel_v = 0.0f;
      this->area_px = 0ul;
      this->color_r = 0;
      this->color_g = 0;
      this->color_b = 0;
    }
  }

  explicit LedDetection_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : bearing(_alloc, _init)
  {
    if (rosidl_runtime_cpp::MessageInitialization::ALL == _init ||
      rosidl_runtime_cpp::MessageInitialization::ZERO == _init)
    {
      this->pixel_u = 0.0f;
      this->pixel_v = 0.0f;
      this->area_px = 0ul;
      this->color_r = 0;
      this->color_g = 0;
      this->color_b = 0;
    }
  }

  // field types and members
  using _pixel_u_type =
    float;
  _pixel_u_type pixel_u;
  using _pixel_v_type =
    float;
  _pixel_v_type pixel_v;
  using _area_px_type =
    uint32_t;
  _area_px_type area_px;
  using _color_r_type =
    uint8_t;
  _color_r_type color_r;
  using _color_g_type =
    uint8_t;
  _color_g_type color_g;
  using _color_b_type =
    uint8_t;
  _color_b_type color_b;
  using _bearing_type =
    geometry_msgs::msg::Vector3_<ContainerAllocator>;
  _bearing_type bearing;

  // setters for named parameter idiom
  Type & set__pixel_u(
    const float & _arg)
  {
    this->pixel_u = _arg;
    return *this;
  }
  Type & set__pixel_v(
    const float & _arg)
  {
    this->pixel_v = _arg;
    return *this;
  }
  Type & set__area_px(
    const uint32_t & _arg)
  {
    this->area_px = _arg;
    return *this;
  }
  Type & set__color_r(
    const uint8_t & _arg)
  {
    this->color_r = _arg;
    return *this;
  }
  Type & set__color_g(
    const uint8_t & _arg)
  {
    this->color_g = _arg;
    return *this;
  }
  Type & set__color_b(
    const uint8_t & _arg)
  {
    this->color_b = _arg;
    return *this;
  }
  Type & set__bearing(
    const geometry_msgs::msg::Vector3_<ContainerAllocator> & _arg)
  {
    this->bearing = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rover_perception_msgs::msg::LedDetection_<ContainerAllocator> *;
  using ConstRawPtr =
    const rover_perception_msgs::msg::LedDetection_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rover_perception_msgs::msg::LedDetection_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rover_perception_msgs::msg::LedDetection_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rover_perception_msgs::msg::LedDetection_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rover_perception_msgs::msg::LedDetection_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rover_perception_msgs::msg::LedDetection_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rover_perception_msgs::msg::LedDetection_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rover_perception_msgs::msg::LedDetection_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rover_perception_msgs::msg::LedDetection_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rover_perception_msgs__msg__LedDetection
    std::shared_ptr<rover_perception_msgs::msg::LedDetection_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rover_perception_msgs__msg__LedDetection
    std::shared_ptr<rover_perception_msgs::msg::LedDetection_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const LedDetection_ & other) const
  {
    if (this->pixel_u != other.pixel_u) {
      return false;
    }
    if (this->pixel_v != other.pixel_v) {
      return false;
    }
    if (this->area_px != other.area_px) {
      return false;
    }
    if (this->color_r != other.color_r) {
      return false;
    }
    if (this->color_g != other.color_g) {
      return false;
    }
    if (this->color_b != other.color_b) {
      return false;
    }
    if (this->bearing != other.bearing) {
      return false;
    }
    return true;
  }
  bool operator!=(const LedDetection_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct LedDetection_

// alias to use template instance with default allocator
using LedDetection =
  rover_perception_msgs::msg::LedDetection_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace rover_perception_msgs

#endif  // ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__STRUCT_HPP_
