// generated from rosidl_typesupport_introspection_c/resource/idl__type_support.c.em
// with input from rover_perception_msgs:msg/TerrainGrid.idl
// generated code does not contain a copyright notice

#include <stddef.h>
#include "rover_perception_msgs/msg/detail/terrain_grid__rosidl_typesupport_introspection_c.h"
#include "rover_perception_msgs/msg/rosidl_typesupport_introspection_c__visibility_control.h"
#include "rosidl_typesupport_introspection_c/field_types.h"
#include "rosidl_typesupport_introspection_c/identifier.h"
#include "rosidl_typesupport_introspection_c/message_introspection.h"
#include "rover_perception_msgs/msg/detail/terrain_grid__functions.h"
#include "rover_perception_msgs/msg/detail/terrain_grid__struct.h"


// Include directives for member types
// Member `header`
#include "std_msgs/msg/header.h"
// Member `header`
#include "std_msgs/msg/detail/header__rosidl_typesupport_introspection_c.h"
// Member `info`
#include "nav_msgs/msg/map_meta_data.h"
// Member `info`
#include "nav_msgs/msg/detail/map_meta_data__rosidl_typesupport_introspection_c.h"
// Member `traversability`
// Member `min_z`
// Member `max_z`
// Member `mean_z`
// Member `roughness`
// Member `plane_slope_deg`
// Member `point_count`
// Member `total_weight`
#include "rosidl_runtime_c/primitives_sequence_functions.h"

#ifdef __cplusplus
extern "C"
{
#endif

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_init_function(
  void * message_memory, enum rosidl_runtime_c__message_initialization _init)
{
  // TODO(karsten1987): initializers are not yet implemented for typesupport c
  // see https://github.com/ros2/ros2/issues/397
  (void) _init;
  rover_perception_msgs__msg__TerrainGrid__init(message_memory);
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_fini_function(void * message_memory)
{
  rover_perception_msgs__msg__TerrainGrid__fini(message_memory);
}

size_t rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__traversability(
  const void * untyped_member)
{
  const rosidl_runtime_c__int8__Sequence * member =
    (const rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return member->size;
}

const void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__traversability(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__int8__Sequence * member =
    (const rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__traversability(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__int8__Sequence * member =
    (rosidl_runtime_c__int8__Sequence *)(untyped_member);
  return &member->data[index];
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__traversability(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int8_t * item =
    ((const int8_t *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__traversability(untyped_member, index));
  int8_t * value =
    (int8_t *)(untyped_value);
  *value = *item;
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__traversability(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int8_t * item =
    ((int8_t *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__traversability(untyped_member, index));
  const int8_t * value =
    (const int8_t *)(untyped_value);
  *item = *value;
}

bool rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__traversability(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__int8__Sequence * member =
    (rosidl_runtime_c__int8__Sequence *)(untyped_member);
  rosidl_runtime_c__int8__Sequence__fini(member);
  return rosidl_runtime_c__int8__Sequence__init(member, size);
}

size_t rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__min_z(
  const void * untyped_member)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return member->size;
}

const void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__min_z(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__min_z(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__min_z(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__min_z(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__min_z(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__min_z(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

bool rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__min_z(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  rosidl_runtime_c__float__Sequence__fini(member);
  return rosidl_runtime_c__float__Sequence__init(member, size);
}

size_t rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__max_z(
  const void * untyped_member)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return member->size;
}

const void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__max_z(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__max_z(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__max_z(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__max_z(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__max_z(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__max_z(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

bool rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__max_z(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  rosidl_runtime_c__float__Sequence__fini(member);
  return rosidl_runtime_c__float__Sequence__init(member, size);
}

size_t rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__mean_z(
  const void * untyped_member)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return member->size;
}

const void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__mean_z(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__mean_z(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__mean_z(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__mean_z(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__mean_z(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__mean_z(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

bool rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__mean_z(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  rosidl_runtime_c__float__Sequence__fini(member);
  return rosidl_runtime_c__float__Sequence__init(member, size);
}

size_t rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__roughness(
  const void * untyped_member)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return member->size;
}

const void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__roughness(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__roughness(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__roughness(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__roughness(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__roughness(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__roughness(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

bool rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__roughness(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  rosidl_runtime_c__float__Sequence__fini(member);
  return rosidl_runtime_c__float__Sequence__init(member, size);
}

size_t rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__plane_slope_deg(
  const void * untyped_member)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return member->size;
}

const void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__plane_slope_deg(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__plane_slope_deg(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__plane_slope_deg(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__plane_slope_deg(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__plane_slope_deg(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__plane_slope_deg(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

bool rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__plane_slope_deg(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  rosidl_runtime_c__float__Sequence__fini(member);
  return rosidl_runtime_c__float__Sequence__init(member, size);
}

size_t rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__point_count(
  const void * untyped_member)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return member->size;
}

const void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__point_count(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__int32__Sequence * member =
    (const rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__point_count(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  return &member->data[index];
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__point_count(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const int32_t * item =
    ((const int32_t *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__point_count(untyped_member, index));
  int32_t * value =
    (int32_t *)(untyped_value);
  *value = *item;
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__point_count(
  void * untyped_member, size_t index, const void * untyped_value)
{
  int32_t * item =
    ((int32_t *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__point_count(untyped_member, index));
  const int32_t * value =
    (const int32_t *)(untyped_value);
  *item = *value;
}

bool rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__point_count(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__int32__Sequence * member =
    (rosidl_runtime_c__int32__Sequence *)(untyped_member);
  rosidl_runtime_c__int32__Sequence__fini(member);
  return rosidl_runtime_c__int32__Sequence__init(member, size);
}

size_t rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__total_weight(
  const void * untyped_member)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return member->size;
}

const void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__total_weight(
  const void * untyped_member, size_t index)
{
  const rosidl_runtime_c__float__Sequence * member =
    (const rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void * rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__total_weight(
  void * untyped_member, size_t index)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  return &member->data[index];
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__total_weight(
  const void * untyped_member, size_t index, void * untyped_value)
{
  const float * item =
    ((const float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__total_weight(untyped_member, index));
  float * value =
    (float *)(untyped_value);
  *value = *item;
}

void rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__total_weight(
  void * untyped_member, size_t index, const void * untyped_value)
{
  float * item =
    ((float *)
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__total_weight(untyped_member, index));
  const float * value =
    (const float *)(untyped_value);
  *item = *value;
}

bool rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__total_weight(
  void * untyped_member, size_t size)
{
  rosidl_runtime_c__float__Sequence * member =
    (rosidl_runtime_c__float__Sequence *)(untyped_member);
  rosidl_runtime_c__float__Sequence__fini(member);
  return rosidl_runtime_c__float__Sequence__init(member, size);
}

static rosidl_typesupport_introspection_c__MessageMember rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_message_member_array[10] = {
  {
    "header",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__TerrainGrid, header),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "info",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_MESSAGE,  // type
    0,  // upper bound of string
    NULL,  // members of sub message (initialized later)
    false,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__TerrainGrid, info),  // bytes offset in struct
    NULL,  // default value
    NULL,  // size() function pointer
    NULL,  // get_const(index) function pointer
    NULL,  // get(index) function pointer
    NULL,  // fetch(index, &value) function pointer
    NULL,  // assign(index, value) function pointer
    NULL  // resize(index) function pointer
  },
  {
    "traversability",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT8,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__TerrainGrid, traversability),  // bytes offset in struct
    NULL,  // default value
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__traversability,  // size() function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__traversability,  // get_const(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__traversability,  // get(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__traversability,  // fetch(index, &value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__traversability,  // assign(index, value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__traversability  // resize(index) function pointer
  },
  {
    "min_z",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__TerrainGrid, min_z),  // bytes offset in struct
    NULL,  // default value
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__min_z,  // size() function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__min_z,  // get_const(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__min_z,  // get(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__min_z,  // fetch(index, &value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__min_z,  // assign(index, value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__min_z  // resize(index) function pointer
  },
  {
    "max_z",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__TerrainGrid, max_z),  // bytes offset in struct
    NULL,  // default value
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__max_z,  // size() function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__max_z,  // get_const(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__max_z,  // get(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__max_z,  // fetch(index, &value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__max_z,  // assign(index, value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__max_z  // resize(index) function pointer
  },
  {
    "mean_z",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__TerrainGrid, mean_z),  // bytes offset in struct
    NULL,  // default value
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__mean_z,  // size() function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__mean_z,  // get_const(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__mean_z,  // get(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__mean_z,  // fetch(index, &value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__mean_z,  // assign(index, value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__mean_z  // resize(index) function pointer
  },
  {
    "roughness",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__TerrainGrid, roughness),  // bytes offset in struct
    NULL,  // default value
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__roughness,  // size() function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__roughness,  // get_const(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__roughness,  // get(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__roughness,  // fetch(index, &value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__roughness,  // assign(index, value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__roughness  // resize(index) function pointer
  },
  {
    "plane_slope_deg",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__TerrainGrid, plane_slope_deg),  // bytes offset in struct
    NULL,  // default value
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__plane_slope_deg,  // size() function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__plane_slope_deg,  // get_const(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__plane_slope_deg,  // get(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__plane_slope_deg,  // fetch(index, &value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__plane_slope_deg,  // assign(index, value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__plane_slope_deg  // resize(index) function pointer
  },
  {
    "point_count",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_INT32,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__TerrainGrid, point_count),  // bytes offset in struct
    NULL,  // default value
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__point_count,  // size() function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__point_count,  // get_const(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__point_count,  // get(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__point_count,  // fetch(index, &value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__point_count,  // assign(index, value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__point_count  // resize(index) function pointer
  },
  {
    "total_weight",  // name
    rosidl_typesupport_introspection_c__ROS_TYPE_FLOAT,  // type
    0,  // upper bound of string
    NULL,  // members of sub message
    true,  // is array
    0,  // array size
    false,  // is upper bound
    offsetof(rover_perception_msgs__msg__TerrainGrid, total_weight),  // bytes offset in struct
    NULL,  // default value
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__size_function__TerrainGrid__total_weight,  // size() function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_const_function__TerrainGrid__total_weight,  // get_const(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__get_function__TerrainGrid__total_weight,  // get(index) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__fetch_function__TerrainGrid__total_weight,  // fetch(index, &value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__assign_function__TerrainGrid__total_weight,  // assign(index, value) function pointer
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__resize_function__TerrainGrid__total_weight  // resize(index) function pointer
  }
};

static const rosidl_typesupport_introspection_c__MessageMembers rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_message_members = {
  "rover_perception_msgs__msg",  // message namespace
  "TerrainGrid",  // message name
  10,  // number of fields
  sizeof(rover_perception_msgs__msg__TerrainGrid),
  rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_message_member_array,  // message members
  rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_init_function,  // function to initialize message memory (memory has to be allocated)
  rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_fini_function  // function to terminate message instance (will not free memory)
};

// this is not const since it must be initialized on first access
// since C does not allow non-integral compile-time constants
static rosidl_message_type_support_t rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_message_type_support_handle = {
  0,
  &rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_message_members,
  get_message_typesupport_handle_function,
};

ROSIDL_TYPESUPPORT_INTROSPECTION_C_EXPORT_rover_perception_msgs
const rosidl_message_type_support_t *
ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, rover_perception_msgs, msg, TerrainGrid)() {
  rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_message_member_array[0].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, std_msgs, msg, Header)();
  rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_message_member_array[1].members_ =
    ROSIDL_TYPESUPPORT_INTERFACE__MESSAGE_SYMBOL_NAME(rosidl_typesupport_introspection_c, nav_msgs, msg, MapMetaData)();
  if (!rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_message_type_support_handle.typesupport_identifier) {
    rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_message_type_support_handle.typesupport_identifier =
      rosidl_typesupport_introspection_c__identifier;
  }
  return &rover_perception_msgs__msg__TerrainGrid__rosidl_typesupport_introspection_c__TerrainGrid_message_type_support_handle;
}
#ifdef __cplusplus
}
#endif
