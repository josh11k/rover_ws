// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rover_perception_msgs:msg/LedDetection.idl
// generated code does not contain a copyright notice

#ifndef ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__STRUCT_H_
#define ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'bearing'
#include "geometry_msgs/msg/detail/vector3__struct.h"

/// Struct defined in msg/LedDetection in the package rover_perception_msgs.
/**
  * A single LED blob detected in a mono-camera image by led_detector_node.
 */
typedef struct rover_perception_msgs__msg__LedDetection
{
  /// blob centroid, image x (pixels)
  float pixel_u;
  /// blob centroid, image y (pixels)
  float pixel_v;
  /// blob size, connected-component pixel count
  uint32_t area_px;
  /// mean color of the blob (0-255) -- lets a future
  uint8_t color_r;
  /// consumer match a detection to a known robot's
  uint8_t color_g;
  /// LED color, if robots use distinct colors
  uint8_t color_b;
  /// Unit bearing vector to the blob, in the camera's optical frame (REP-103:
  /// Z forward, X right, Y down). Pre-converted from (pixel_u, pixel_v) via the
  /// camera intrinsics, so downstream nodes can rotate it into base_link with
  /// the same static TF used for the point clouds, without needing pixel
  /// coordinates or intrinsics again. A mono camera alone only gives a
  /// *direction*, not a distance -- turning this into a full 3D position needs
  /// extra information (e.g. known LED spacing, or multi-view triangulation),
  /// which is out of scope for this node.
  geometry_msgs__msg__Vector3 bearing;
} rover_perception_msgs__msg__LedDetection;

// Struct for a sequence of rover_perception_msgs__msg__LedDetection.
typedef struct rover_perception_msgs__msg__LedDetection__Sequence
{
  rover_perception_msgs__msg__LedDetection * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rover_perception_msgs__msg__LedDetection__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION__STRUCT_H_
