// generated from rosidl_generator_cpp/resource/idl__struct.hpp.em
// with input from rover_perception_msgs:msg/TerrainGrid.idl
// generated code does not contain a copyright notice

#ifndef ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__STRUCT_HPP_
#define ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__STRUCT_HPP_

#include <algorithm>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "rosidl_runtime_cpp/bounded_vector.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.hpp"
// Member 'info'
#include "nav_msgs/msg/detail/map_meta_data__struct.hpp"

#ifndef _WIN32
# define DEPRECATED__rover_perception_msgs__msg__TerrainGrid __attribute__((deprecated))
#else
# define DEPRECATED__rover_perception_msgs__msg__TerrainGrid __declspec(deprecated)
#endif

namespace rover_perception_msgs
{

namespace msg
{

// message struct
template<class ContainerAllocator>
struct TerrainGrid_
{
  using Type = TerrainGrid_<ContainerAllocator>;

  explicit TerrainGrid_(rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_init),
    info(_init)
  {
    (void)_init;
  }

  explicit TerrainGrid_(const ContainerAllocator & _alloc, rosidl_runtime_cpp::MessageInitialization _init = rosidl_runtime_cpp::MessageInitialization::ALL)
  : header(_alloc, _init),
    info(_alloc, _init)
  {
    (void)_init;
  }

  // field types and members
  using _header_type =
    std_msgs::msg::Header_<ContainerAllocator>;
  _header_type header;
  using _info_type =
    nav_msgs::msg::MapMetaData_<ContainerAllocator>;
  _info_type info;
  using _traversability_type =
    std::vector<int8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int8_t>>;
  _traversability_type traversability;
  using _min_z_type =
    std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>>;
  _min_z_type min_z;
  using _max_z_type =
    std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>>;
  _max_z_type max_z;
  using _mean_z_type =
    std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>>;
  _mean_z_type mean_z;
  using _roughness_type =
    std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>>;
  _roughness_type roughness;
  using _plane_slope_deg_type =
    std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>>;
  _plane_slope_deg_type plane_slope_deg;
  using _point_count_type =
    std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>>;
  _point_count_type point_count;
  using _total_weight_type =
    std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>>;
  _total_weight_type total_weight;

  // setters for named parameter idiom
  Type & set__header(
    const std_msgs::msg::Header_<ContainerAllocator> & _arg)
  {
    this->header = _arg;
    return *this;
  }
  Type & set__info(
    const nav_msgs::msg::MapMetaData_<ContainerAllocator> & _arg)
  {
    this->info = _arg;
    return *this;
  }
  Type & set__traversability(
    const std::vector<int8_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int8_t>> & _arg)
  {
    this->traversability = _arg;
    return *this;
  }
  Type & set__min_z(
    const std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>> & _arg)
  {
    this->min_z = _arg;
    return *this;
  }
  Type & set__max_z(
    const std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>> & _arg)
  {
    this->max_z = _arg;
    return *this;
  }
  Type & set__mean_z(
    const std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>> & _arg)
  {
    this->mean_z = _arg;
    return *this;
  }
  Type & set__roughness(
    const std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>> & _arg)
  {
    this->roughness = _arg;
    return *this;
  }
  Type & set__plane_slope_deg(
    const std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>> & _arg)
  {
    this->plane_slope_deg = _arg;
    return *this;
  }
  Type & set__point_count(
    const std::vector<int32_t, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<int32_t>> & _arg)
  {
    this->point_count = _arg;
    return *this;
  }
  Type & set__total_weight(
    const std::vector<float, typename std::allocator_traits<ContainerAllocator>::template rebind_alloc<float>> & _arg)
  {
    this->total_weight = _arg;
    return *this;
  }

  // constant declarations

  // pointer types
  using RawPtr =
    rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator> *;
  using ConstRawPtr =
    const rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator> *;
  using SharedPtr =
    std::shared_ptr<rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator>>;
  using ConstSharedPtr =
    std::shared_ptr<rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator> const>;

  template<typename Deleter = std::default_delete<
      rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator>>>
  using UniquePtrWithDeleter =
    std::unique_ptr<rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator>, Deleter>;

  using UniquePtr = UniquePtrWithDeleter<>;

  template<typename Deleter = std::default_delete<
      rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator>>>
  using ConstUniquePtrWithDeleter =
    std::unique_ptr<rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator> const, Deleter>;
  using ConstUniquePtr = ConstUniquePtrWithDeleter<>;

  using WeakPtr =
    std::weak_ptr<rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator>>;
  using ConstWeakPtr =
    std::weak_ptr<rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator> const>;

  // pointer types similar to ROS 1, use SharedPtr / ConstSharedPtr instead
  // NOTE: Can't use 'using' here because GNU C++ can't parse attributes properly
  typedef DEPRECATED__rover_perception_msgs__msg__TerrainGrid
    std::shared_ptr<rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator>>
    Ptr;
  typedef DEPRECATED__rover_perception_msgs__msg__TerrainGrid
    std::shared_ptr<rover_perception_msgs::msg::TerrainGrid_<ContainerAllocator> const>
    ConstPtr;

  // comparison operators
  bool operator==(const TerrainGrid_ & other) const
  {
    if (this->header != other.header) {
      return false;
    }
    if (this->info != other.info) {
      return false;
    }
    if (this->traversability != other.traversability) {
      return false;
    }
    if (this->min_z != other.min_z) {
      return false;
    }
    if (this->max_z != other.max_z) {
      return false;
    }
    if (this->mean_z != other.mean_z) {
      return false;
    }
    if (this->roughness != other.roughness) {
      return false;
    }
    if (this->plane_slope_deg != other.plane_slope_deg) {
      return false;
    }
    if (this->point_count != other.point_count) {
      return false;
    }
    if (this->total_weight != other.total_weight) {
      return false;
    }
    return true;
  }
  bool operator!=(const TerrainGrid_ & other) const
  {
    return !this->operator==(other);
  }
};  // struct TerrainGrid_

// alias to use template instance with default allocator
using TerrainGrid =
  rover_perception_msgs::msg::TerrainGrid_<std::allocator<void>>;

// constant definitions

}  // namespace msg

}  // namespace rover_perception_msgs

#endif  // ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__STRUCT_HPP_
