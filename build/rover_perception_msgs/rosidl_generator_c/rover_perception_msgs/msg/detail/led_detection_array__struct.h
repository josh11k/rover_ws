// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from rover_perception_msgs:msg/LedDetectionArray.idl
// generated code does not contain a copyright notice

#ifndef ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION_ARRAY__STRUCT_H_
#define ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION_ARRAY__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'header'
#include "std_msgs/msg/detail/header__struct.h"
// Member 'detections'
#include "rover_perception_msgs/msg/detail/led_detection__struct.h"

/// Struct defined in msg/LedDetectionArray in the package rover_perception_msgs.
/**
  * All LED blobs detected in one mono-camera frame.
  *
  * header.stamp/frame_id are copied from the source image (frame_id =
  * mono_cam_optical_frame), so detections can be time- and frame-correlated
  * with everything else in the pipeline. Empty `detections` is a normal,
  * valid message (no LEDs visible this frame) -- not an error condition.
 */
typedef struct rover_perception_msgs__msg__LedDetectionArray
{
  std_msgs__msg__Header header;
  rover_perception_msgs__msg__LedDetection__Sequence detections;
} rover_perception_msgs__msg__LedDetectionArray;

// Struct for a sequence of rover_perception_msgs__msg__LedDetectionArray.
typedef struct rover_perception_msgs__msg__LedDetectionArray__Sequence
{
  rover_perception_msgs__msg__LedDetectionArray * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} rover_perception_msgs__msg__LedDetectionArray__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION_ARRAY__STRUCT_H_
