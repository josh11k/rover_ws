// generated from rosidl_generator_cpp/resource/idl__builder.hpp.em
// with input from rover_perception_msgs:msg/TerrainGrid.idl
// generated code does not contain a copyright notice

#ifndef ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__BUILDER_HPP_
#define ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__BUILDER_HPP_

#include <algorithm>
#include <utility>

#include "rover_perception_msgs/msg/detail/terrain_grid__struct.hpp"
#include "rosidl_runtime_cpp/message_initialization.hpp"


namespace rover_perception_msgs
{

namespace msg
{

namespace builder
{

class Init_TerrainGrid_total_weight
{
public:
  explicit Init_TerrainGrid_total_weight(::rover_perception_msgs::msg::TerrainGrid & msg)
  : msg_(msg)
  {}
  ::rover_perception_msgs::msg::TerrainGrid total_weight(::rover_perception_msgs::msg::TerrainGrid::_total_weight_type arg)
  {
    msg_.total_weight = std::move(arg);
    return std::move(msg_);
  }

private:
  ::rover_perception_msgs::msg::TerrainGrid msg_;
};

class Init_TerrainGrid_point_count
{
public:
  explicit Init_TerrainGrid_point_count(::rover_perception_msgs::msg::TerrainGrid & msg)
  : msg_(msg)
  {}
  Init_TerrainGrid_total_weight point_count(::rover_perception_msgs::msg::TerrainGrid::_point_count_type arg)
  {
    msg_.point_count = std::move(arg);
    return Init_TerrainGrid_total_weight(msg_);
  }

private:
  ::rover_perception_msgs::msg::TerrainGrid msg_;
};

class Init_TerrainGrid_plane_slope_deg
{
public:
  explicit Init_TerrainGrid_plane_slope_deg(::rover_perception_msgs::msg::TerrainGrid & msg)
  : msg_(msg)
  {}
  Init_TerrainGrid_point_count plane_slope_deg(::rover_perception_msgs::msg::TerrainGrid::_plane_slope_deg_type arg)
  {
    msg_.plane_slope_deg = std::move(arg);
    return Init_TerrainGrid_point_count(msg_);
  }

private:
  ::rover_perception_msgs::msg::TerrainGrid msg_;
};

class Init_TerrainGrid_roughness
{
public:
  explicit Init_TerrainGrid_roughness(::rover_perception_msgs::msg::TerrainGrid & msg)
  : msg_(msg)
  {}
  Init_TerrainGrid_plane_slope_deg roughness(::rover_perception_msgs::msg::TerrainGrid::_roughness_type arg)
  {
    msg_.roughness = std::move(arg);
    return Init_TerrainGrid_plane_slope_deg(msg_);
  }

private:
  ::rover_perception_msgs::msg::TerrainGrid msg_;
};

class Init_TerrainGrid_mean_z
{
public:
  explicit Init_TerrainGrid_mean_z(::rover_perception_msgs::msg::TerrainGrid & msg)
  : msg_(msg)
  {}
  Init_TerrainGrid_roughness mean_z(::rover_perception_msgs::msg::TerrainGrid::_mean_z_type arg)
  {
    msg_.mean_z = std::move(arg);
    return Init_TerrainGrid_roughness(msg_);
  }

private:
  ::rover_perception_msgs::msg::TerrainGrid msg_;
};

class Init_TerrainGrid_max_z
{
public:
  explicit Init_TerrainGrid_max_z(::rover_perception_msgs::msg::TerrainGrid & msg)
  : msg_(msg)
  {}
  Init_TerrainGrid_mean_z max_z(::rover_perception_msgs::msg::TerrainGrid::_max_z_type arg)
  {
    msg_.max_z = std::move(arg);
    return Init_TerrainGrid_mean_z(msg_);
  }

private:
  ::rover_perception_msgs::msg::TerrainGrid msg_;
};

class Init_TerrainGrid_min_z
{
public:
  explicit Init_TerrainGrid_min_z(::rover_perception_msgs::msg::TerrainGrid & msg)
  : msg_(msg)
  {}
  Init_TerrainGrid_max_z min_z(::rover_perception_msgs::msg::TerrainGrid::_min_z_type arg)
  {
    msg_.min_z = std::move(arg);
    return Init_TerrainGrid_max_z(msg_);
  }

private:
  ::rover_perception_msgs::msg::TerrainGrid msg_;
};

class Init_TerrainGrid_traversability
{
public:
  explicit Init_TerrainGrid_traversability(::rover_perception_msgs::msg::TerrainGrid & msg)
  : msg_(msg)
  {}
  Init_TerrainGrid_min_z traversability(::rover_perception_msgs::msg::TerrainGrid::_traversability_type arg)
  {
    msg_.traversability = std::move(arg);
    return Init_TerrainGrid_min_z(msg_);
  }

private:
  ::rover_perception_msgs::msg::TerrainGrid msg_;
};

class Init_TerrainGrid_info
{
public:
  explicit Init_TerrainGrid_info(::rover_perception_msgs::msg::TerrainGrid & msg)
  : msg_(msg)
  {}
  Init_TerrainGrid_traversability info(::rover_perception_msgs::msg::TerrainGrid::_info_type arg)
  {
    msg_.info = std::move(arg);
    return Init_TerrainGrid_traversability(msg_);
  }

private:
  ::rover_perception_msgs::msg::TerrainGrid msg_;
};

class Init_TerrainGrid_header
{
public:
  Init_TerrainGrid_header()
  : msg_(::rosidl_runtime_cpp::MessageInitialization::SKIP)
  {}
  Init_TerrainGrid_info header(::rover_perception_msgs::msg::TerrainGrid::_header_type arg)
  {
    msg_.header = std::move(arg);
    return Init_TerrainGrid_info(msg_);
  }

private:
  ::rover_perception_msgs::msg::TerrainGrid msg_;
};

}  // namespace builder

}  // namespace msg

template<typename MessageType>
auto build();

template<>
inline
auto build<::rover_perception_msgs::msg::TerrainGrid>()
{
  return rover_perception_msgs::msg::builder::Init_TerrainGrid_header();
}

}  // namespace rover_perception_msgs

#endif  // ROVER_PERCEPTION_MSGS__MSG__DETAIL__TERRAIN_GRID__BUILDER_HPP_
