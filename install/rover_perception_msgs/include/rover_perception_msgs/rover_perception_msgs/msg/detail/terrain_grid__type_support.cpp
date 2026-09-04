// generated from rosidl_typesupport_introspection_cpp/resource/idl__type_support.cpp.em
// with input from rover_perception_msgs:msg/TerrainGrid.idl
// generated code does not contain a copyright notice

#include "array"
#include "cstddef"
#include "string"
#include "vector"
#include "rosidl_runtime_c/message_type_support_struct.h"
#include "rosidl_typesupport_cpp/message_type_support.hpp"
#include "rosidl_typesupport_interface/macros.h"
#include "rover_perception_msgs/msg/detail/terrain_grid__struct.hpp"
#include "rosidl_typesupport_introspection_cpp/field_types.hpp"
#include "rosidl_typesupport_introspection_cpp/identifier.hpp"
#include "rosidl_typesupport_introspection_cpp/message_introspection.hpp"
#include "rosidl_typesupport_introspection_cpp/message_type_support_decl.hpp"
#include "rosidl_typesupport_introspection_cpp/visibility_control.h"

namespace rover_perception_msgs
{

namespace msg
{

namespace rosidl_typesupport_introspection_cpp
{

void TerrainGrid_init_function(
  void * message_memory, rosidl_runtime_cpp::MessageInitialization _init)
{
  new (message_memory) rover_perception_msgs::msg::TerrainGrid(_init);
}

void TerrainGrid_fini_function(void * message_memory)
{
  auto typed_message = static_cast<rover_perception_msgs::msg::TerrainGrid *>(message_memory);
  typed_message->~TerrainGrid();
}

size_t size_function__TerrainGrid__traversability(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<int8_t> *>(untyped_member);
  return member->size();
}

const void * get_const_function__TerrainGrid__traversability(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<int8_t> *>(untyped_member);
  return &member[index];
}

void * get_function__TerrainGrid__traversability(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<int8_t> *>(untyped_member);
  return &member[index];
}

void fetch_function__TerrainGrid__traversability(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int8_t *>(
    get_const_function__TerrainGrid__traversability(untyped_member, index));
  auto & value = *reinterpret_cast<int8_t *>(untyped_value);
  value = item;
}

void assign_function__TerrainGrid__traversability(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int8_t *>(
    get_function__TerrainGrid__traversability(untyped_member, index));
  const auto & value = *reinterpret_cast<const int8_t *>(untyped_value);
  item = value;
}

void resize_function__TerrainGrid__traversability(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<int8_t> *>(untyped_member);
  member->resize(size);
}

size_t size_function__TerrainGrid__min_z(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<float> *>(untyped_member);
  return member->size();
}

const void * get_const_function__TerrainGrid__min_z(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<float> *>(untyped_member);
  return &member[index];
}

void * get_function__TerrainGrid__min_z(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<float> *>(untyped_member);
  return &member[index];
}

void fetch_function__TerrainGrid__min_z(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const float *>(
    get_const_function__TerrainGrid__min_z(untyped_member, index));
  auto & value = *reinterpret_cast<float *>(untyped_value);
  value = item;
}

void assign_function__TerrainGrid__min_z(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<float *>(
    get_function__TerrainGrid__min_z(untyped_member, index));
  const auto & value = *reinterpret_cast<const float *>(untyped_value);
  item = value;
}

void resize_function__TerrainGrid__min_z(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<float> *>(untyped_member);
  member->resize(size);
}

size_t size_function__TerrainGrid__max_z(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<float> *>(untyped_member);
  return member->size();
}

const void * get_const_function__TerrainGrid__max_z(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<float> *>(untyped_member);
  return &member[index];
}

void * get_function__TerrainGrid__max_z(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<float> *>(untyped_member);
  return &member[index];
}

void fetch_function__TerrainGrid__max_z(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const float *>(
    get_const_function__TerrainGrid__max_z(untyped_member, index));
  auto & value = *reinterpret_cast<float *>(untyped_value);
  value = item;
}

void assign_function__TerrainGrid__max_z(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<float *>(
    get_function__TerrainGrid__max_z(untyped_member, index));
  const auto & value = *reinterpret_cast<const float *>(untyped_value);
  item = value;
}

void resize_function__TerrainGrid__max_z(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<float> *>(untyped_member);
  member->resize(size);
}

size_t size_function__TerrainGrid__mean_z(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<float> *>(untyped_member);
  return member->size();
}

const void * get_const_function__TerrainGrid__mean_z(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<float> *>(untyped_member);
  return &member[index];
}

void * get_function__TerrainGrid__mean_z(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<float> *>(untyped_member);
  return &member[index];
}

void fetch_function__TerrainGrid__mean_z(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const float *>(
    get_const_function__TerrainGrid__mean_z(untyped_member, index));
  auto & value = *reinterpret_cast<float *>(untyped_value);
  value = item;
}

void assign_function__TerrainGrid__mean_z(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<float *>(
    get_function__TerrainGrid__mean_z(untyped_member, index));
  const auto & value = *reinterpret_cast<const float *>(untyped_value);
  item = value;
}

void resize_function__TerrainGrid__mean_z(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<float> *>(untyped_member);
  member->resize(size);
}

size_t size_function__TerrainGrid__roughness(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<float> *>(untyped_member);
  return member->size();
}

const void * get_const_function__TerrainGrid__roughness(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<float> *>(untyped_member);
  return &member[index];
}

void * get_function__TerrainGrid__roughness(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<float> *>(untyped_member);
  return &member[index];
}

void fetch_function__TerrainGrid__roughness(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const float *>(
    get_const_function__TerrainGrid__roughness(untyped_member, index));
  auto & value = *reinterpret_cast<float *>(untyped_value);
  value = item;
}

void assign_function__TerrainGrid__roughness(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<float *>(
    get_function__TerrainGrid__roughness(untyped_member, index));
  const auto & value = *reinterpret_cast<const float *>(untyped_value);
  item = value;
}

void resize_function__TerrainGrid__roughness(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<float> *>(untyped_member);
  member->resize(size);
}

size_t size_function__TerrainGrid__plane_slope_deg(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<float> *>(untyped_member);
  return member->size();
}

const void * get_const_function__TerrainGrid__plane_slope_deg(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<float> *>(untyped_member);
  return &member[index];
}

void * get_function__TerrainGrid__plane_slope_deg(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<float> *>(untyped_member);
  return &member[index];
}

void fetch_function__TerrainGrid__plane_slope_deg(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const float *>(
    get_const_function__TerrainGrid__plane_slope_deg(untyped_member, index));
  auto & value = *reinterpret_cast<float *>(untyped_value);
  value = item;
}

void assign_function__TerrainGrid__plane_slope_deg(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<float *>(
    get_function__TerrainGrid__plane_slope_deg(untyped_member, index));
  const auto & value = *reinterpret_cast<const float *>(untyped_value);
  item = value;
}

void resize_function__TerrainGrid__plane_slope_deg(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<float> *>(untyped_member);
  member->resize(size);
}

size_t size_function__TerrainGrid__point_count(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return member->size();
}

const void * get_const_function__TerrainGrid__point_count(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void * get_function__TerrainGrid__point_count(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  return &member[index];
}

void fetch_function__TerrainGrid__point_count(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const int32_t *>(
    get_const_function__TerrainGrid__point_count(untyped_member, index));
  auto & value = *reinterpret_cast<int32_t *>(untyped_value);
  value = item;
}

void assign_function__TerrainGrid__point_count(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<int32_t *>(
    get_function__TerrainGrid__point_count(untyped_member, index));
  const auto & value = *reinterpret_cast<const int32_t *>(untyped_value);
  item = value;
}

void resize_function__TerrainGrid__point_count(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<int32_t> *>(untyped_member);
  member->resize(size);
}

size_t size_function__TerrainGrid__total_weight(const void * untyped_member)
{
  const auto * member = reinterpret_cast<const std::vector<float> *>(untyped_member);
  return member->size();
}

const void * get_const_function__TerrainGrid__total_weight(const void * untyped_member, size_t index)
{
  const auto & member =
    *reinterpret_cast<const std::vector<float> *>(untyped_member);
  return &member[index];
}

void * get_function__TerrainGrid__total_weight(void * untyped_member, size_t index)
{
  auto & member =
    *reinterpret_cast<std::vector<float> *>(untyped_member);
  return &member[index];
}

void fetch_function__TerrainGrid__total_weight(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const auto & item = *reinterpret_cast<const float *>(
    get_const_function__TerrainGrid__total_weight(untyped_member, index));
  auto & value = *reinterpret_cast<float *>(untyped_value);
  value = item;
}

void assign_function__TerrainGrid__total_weight(
  void * untyped_member, size_t index, const void * untyped_value)
{
  auto & item = *reinterpret_cast<float *>(
    get_function__TerrainGrid__total_weight(untyped_member, index));
  const auto & value = *reinterpret_cast<const float *>(untyped_value);
  item = value;
}

void resize_function__TerrainGrid__total_weight(void * untyped_member, size_t size)
{
  auto * member =
    reinterpret_cast<std::vector<float> *>(untyped_member);
  member->resize(size);
}

static const ::rosidl_typesupport_introspection_cpp::MessageMember TerrainGrid_message_member_array[10] = {
  {
    "header",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<std_msgs::msg::Header>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs::msg::TerrainGrid, header),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "info",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    ::rosidl_typesupport_introspection_cpp::get_message_type_support_handle<nav_msgs::msg::MapMetaData>(),  // members of sub message
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs::msg::TerrainGrid, info),  // bytes offset in struct
    nullptr,  // default value
    nullptr,  // size() function pointer
    nullptr,  // get_const(index) function pointer
    nullptr,  // get(index) function pointer
    nullptr,  // fetch(index, &value) function pointer
    nullptr,  // assign(index, value) function pointer
    nullptr  // resize(index) function pointer
  },
  {
    "traversability",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs::msg::TerrainGrid, traversability),  // bytes offset in struct
    nullptr,  // default value
    size_function__TerrainGrid__traversability,  // size() function pointer
    get_const_function__TerrainGrid__traversability,  // get_const(index) function pointer
    get_function__TerrainGrid__traversability,  // get(index) function pointer
    fetch_function__TerrainGrid__traversability,  // fetch(index, &value) function pointer
    assign_function__TerrainGrid__traversability,  // assign(index, value) function pointer
    resize_function__TerrainGrid__traversability  // resize(index) function pointer
  },
  {
    "min_z",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs::msg::TerrainGrid, min_z),  // bytes offset in struct
    nullptr,  // default value
    size_function__TerrainGrid__min_z,  // size() function pointer
    get_const_function__TerrainGrid__min_z,  // get_const(index) function pointer
    get_function__TerrainGrid__min_z,  // get(index) function pointer
    fetch_function__TerrainGrid__min_z,  // fetch(index, &value) function pointer
    assign_function__TerrainGrid__min_z,  // assign(index, value) function pointer
    resize_function__TerrainGrid__min_z  // resize(index) function pointer
  },
  {
    "max_z",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs::msg::TerrainGrid, max_z),  // bytes offset in struct
    nullptr,  // default value
    size_function__TerrainGrid__max_z,  // size() function pointer
    get_const_function__TerrainGrid__max_z,  // get_const(index) function pointer
    get_function__TerrainGrid__max_z,  // get(index) function pointer
    fetch_function__TerrainGrid__max_z,  // fetch(index, &value) function pointer
    assign_function__TerrainGrid__max_z,  // assign(index, value) function pointer
    resize_function__TerrainGrid__max_z  // resize(index) function pointer
  },
  {
    "mean_z",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs::msg::TerrainGrid, mean_z),  // bytes offset in struct
    nullptr,  // default value
    size_function__TerrainGrid__mean_z,  // size() function pointer
    get_const_function__TerrainGrid__mean_z,  // get_const(index) function pointer
    get_function__TerrainGrid__mean_z,  // get(index) function pointer
    fetch_function__TerrainGrid__mean_z,  // fetch(index, &value) function pointer
    assign_function__TerrainGrid__mean_z,  // assign(index, value) function pointer
    resize_function__TerrainGrid__mean_z  // resize(index) function pointer
  },
  {
    "roughness",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs::msg::TerrainGrid, roughness),  // bytes offset in struct
    nullptr,  // default value
    size_function__TerrainGrid__roughness,  // size() function pointer
    get_const_function__TerrainGrid__roughness,  // get_const(index) function pointer
    get_function__TerrainGrid__roughness,  // get(index) function pointer
    fetch_function__TerrainGrid__roughness,  // fetch(index, &value) function pointer
    assign_function__TerrainGrid__roughness,  // assign(index, value) function pointer
    resize_function__TerrainGrid__roughness  // resize(index) function pointer
  },
  {
    "plane_slope_deg",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs::msg::TerrainGrid, plane_slope_deg),  // bytes offset in struct
    nullptr,  // default value
    size_function__TerrainGrid__plane_slope_deg,  // size() function pointer
    get_const_function__TerrainGrid__plane_slope_deg,  // get_const(index) function pointer
    get_function__TerrainGrid__plane_slope_deg,  // get(index) function pointer
    fetch_function__TerrainGrid__plane_slope_deg,  // fetch(index, &value) function pointer
    assign_function__TerrainGrid__plane_slope_deg,  // assign(index, value) function pointer
    resize_function__TerrainGrid__plane_slope_deg  // resize(index) function pointer
  },
  {
    "point_count",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs::msg::TerrainGrid, point_count),  // bytes offset in struct
    nullptr,  // default value
    size_function__TerrainGrid__point_count,  // size() function pointer
    get_const_function__TerrainGrid__point_count,  // get_const(index) function pointer
    get_function__TerrainGrid__point_count,  // get(index) function pointer
    fetch_function__TerrainGrid__point_count,  // fetch(index, &value) function pointer
    assign_function__TerrainGrid__point_count,  // assign(index, value) function pointer
    resize_function__TerrainGrid__point_count  // resize(index) function pointer
  },
  {
    "total_weight",  // name
    ::rosidl_typesupport_introspection_cpp::ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    nullptr,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs::msg::TerrainGrid, total_weight),  // bytes offset in struct
    nullptr,  // default value
    size_function__TerrainGrid__total_weight,  // size() function pointer
    get_const_function__TerrainGrid__total_weight,  // get_const(index) function pointer
    get_function__TerrainGrid__total_weight,  // get(index) function pointer
    fetch_function__TerrainGrid__total_weight,  // fetch(index, &value) function pointer
    assign_function__TerrainGrid__total_weight,  // assign(index, value) function pointer
    resize_function__TerrainGrid__total_weight  // resize(index) function pointer
  }
};

static const ::rosidl_typesupport_introspection_cpp::MessageMembers TerrainGrid_message_members = {
  "rover_perception_msgs::msg",  // message namespace
  "TerrainGrid",  // message name
  10,  // number of fields
  sizeof(rover_perception_msgs::msg::TerrainGrid),
  TerrainGrid_message_member_array,  // message members
  TerrainGrid_init_function,  // function to initialize message memory (memory has to be allocated)
  TerrainGrid_fini_function  // function to terminate message instance (will not free memory)
};

static const rosidl_message_type_support_t TerrainGrid_message_type_support_handle = {
  ::rosidl_typesupport_introspection_cpp::typesupport_identifier,
  &TerrainGrid_message_members,
  get_message_typesupport_handle_function,
};

}  // namespace rosidl_typesupport_introspection_cpp

}  // namespace msg

}  // namespace rover_perception_msgs


namespace rosidl_typesupport_introspection_cpp
{

template<>
ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
get_message_type_support_handle<rover_perception_msgs::msg::TerrainGrid>()
{
  return &::rover_perception_msgs::msg::rosidl_typesupport_introspection_cpp::TerrainGrid_message_type_support_handle;
}

}  // namespace rosidl_typesupport_introspection_cpp

#ifdef __cplusplus
extern "C"
{
#endif

ROSIDL_TYPESUPPORT_INTROSPECTION_CPP_PUBLIC
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_cpp, rover_perception_msgs, msg, TerrainGrid)() {
  return &::rover_perception_msgs::msg::rosidl_typesupport_introspection_cpp::TerrainGrid_message_type_support_handle;
}

#ifdef __cplusplus
}
#endif
