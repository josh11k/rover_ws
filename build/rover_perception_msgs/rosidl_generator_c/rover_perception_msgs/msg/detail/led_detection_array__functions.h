// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from rover_perception_msgs:msg/LedDetectionArray.idl
// generated code does not contain a copyright notice

#ifndef ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION_ARRAY__FUNCTIONS_H_
#define ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION_ARRAY__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "rover_perception_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "rover_perception_msgs/msg/detail/led_detection_array__struct.h"

/// Initialize msg/LedDetectionArray message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * rover_perception_msgs__msg__LedDetectionArray
 * )) before or use
 * rover_perception_msgs__msg__LedDetectionArray__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
bool
rover_perception_msgs__msg__LedDetectionArray__init(rover_perception_msgs__msg__LedDetectionArray * msg);

/// Finalize msg/LedDetectionArray message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
void
rover_perception_msgs__msg__LedDetectionArray__fini(rover_perception_msgs__msg__LedDetectionArray * msg);

/// Create msg/LedDetectionArray message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * rover_perception_msgs__msg__LedDetectionArray__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
rover_perception_msgs__msg__LedDetectionArray *
rover_perception_msgs__msg__LedDetectionArray__create();

/// Destroy msg/LedDetectionArray message.
/**
 * It calls
 * rover_perception_msgs__msg__LedDetectionArray__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
void
rover_perception_msgs__msg__LedDetectionArray__destroy(rover_perception_msgs__msg__LedDetectionArray * msg);

/// Check for msg/LedDetectionArray message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
bool
rover_perception_msgs__msg__LedDetectionArray__are_equal(const rover_perception_msgs__msg__LedDetectionArray * lhs, const rover_perception_msgs__msg__LedDetectionArray * rhs);

/// Copy a msg/LedDetectionArray message.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source message pointer.
 * \param[out] output The target message pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer is null
 *   or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
bool
rover_perception_msgs__msg__LedDetectionArray__copy(
  const rover_perception_msgs__msg__LedDetectionArray * input,
  rover_perception_msgs__msg__LedDetectionArray * output);

/// Initialize array of msg/LedDetectionArray messages.
/**
 * It allocates the memory for the number of elements and calls
 * rover_perception_msgs__msg__LedDetectionArray__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
bool
rover_perception_msgs__msg__LedDetectionArray__Sequence__init(rover_perception_msgs__msg__LedDetectionArray__Sequence * array, size_t size);

/// Finalize array of msg/LedDetectionArray messages.
/**
 * It calls
 * rover_perception_msgs__msg__LedDetectionArray__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
void
rover_perception_msgs__msg__LedDetectionArray__Sequence__fini(rover_perception_msgs__msg__LedDetectionArray__Sequence * array);

/// Create array of msg/LedDetectionArray messages.
/**
 * It allocates the memory for the array and calls
 * rover_perception_msgs__msg__LedDetectionArray__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
rover_perception_msgs__msg__LedDetectionArray__Sequence *
rover_perception_msgs__msg__LedDetectionArray__Sequence__create(size_t size);

/// Destroy array of msg/LedDetectionArray messages.
/**
 * It calls
 * rover_perception_msgs__msg__LedDetectionArray__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
void
rover_perception_msgs__msg__LedDetectionArray__Sequence__destroy(rover_perception_msgs__msg__LedDetectionArray__Sequence * array);

/// Check for msg/LedDetectionArray message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
bool
rover_perception_msgs__msg__LedDetectionArray__Sequence__are_equal(const rover_perception_msgs__msg__LedDetectionArray__Sequence * lhs, const rover_perception_msgs__msg__LedDetectionArray__Sequence * rhs);

/// Copy an array of msg/LedDetectionArray messages.
/**
 * This functions performs a deep copy, as opposed to the shallow copy that
 * plain assignment yields.
 *
 * \param[in] input The source array pointer.
 * \param[out] output The target array pointer, which must
 *   have been initialized before calling this function.
 * \return true if successful, or false if either pointer
 *   is null or memory allocation fails.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_perception_msgs
bool
rover_perception_msgs__msg__LedDetectionArray__Sequence__copy(
  const rover_perception_msgs__msg__LedDetectionArray__Sequence * input,
  rover_perception_msgs__msg__LedDetectionArray__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // ROVER_PERCEPTION_MSGS__MSG__DETAIL__LED_DETECTION_ARRAY__FUNCTIONS_H_
