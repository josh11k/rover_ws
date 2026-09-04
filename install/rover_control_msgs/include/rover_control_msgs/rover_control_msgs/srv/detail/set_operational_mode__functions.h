// generated from rosidl_generator_c/resource/idl__functions.h.em
// with input from rover_control_msgs:srv/SetOperationalMode.idl
// generated code does not contain a copyright notice

#ifndef ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__FUNCTIONS_H_
#define ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__FUNCTIONS_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stdlib.h>

#include "rosidl_runtime_c/visibility_control.h"
#include "rover_control_msgs/msg/rosidl_generator_c__visibility_control.h"

#include "rover_control_msgs/srv/detail/set_operational_mode__struct.h"

/// Initialize srv/SetOperationalMode message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * rover_control_msgs__srv__SetOperationalMode_Request
 * )) before or use
 * rover_control_msgs__srv__SetOperationalMode_Request__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Request__init(rover_control_msgs__srv__SetOperationalMode_Request * msg);

/// Finalize srv/SetOperationalMode message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
void
rover_control_msgs__srv__SetOperationalMode_Request__fini(rover_control_msgs__srv__SetOperationalMode_Request * msg);

/// Create srv/SetOperationalMode message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * rover_control_msgs__srv__SetOperationalMode_Request__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
rover_control_msgs__srv__SetOperationalMode_Request *
rover_control_msgs__srv__SetOperationalMode_Request__create();

/// Destroy srv/SetOperationalMode message.
/**
 * It calls
 * rover_control_msgs__srv__SetOperationalMode_Request__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
void
rover_control_msgs__srv__SetOperationalMode_Request__destroy(rover_control_msgs__srv__SetOperationalMode_Request * msg);

/// Check for srv/SetOperationalMode message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Request__are_equal(const rover_control_msgs__srv__SetOperationalMode_Request * lhs, const rover_control_msgs__srv__SetOperationalMode_Request * rhs);

/// Copy a srv/SetOperationalMode message.
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
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Request__copy(
  const rover_control_msgs__srv__SetOperationalMode_Request * input,
  rover_control_msgs__srv__SetOperationalMode_Request * output);

/// Initialize array of srv/SetOperationalMode messages.
/**
 * It allocates the memory for the number of elements and calls
 * rover_control_msgs__srv__SetOperationalMode_Request__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__init(rover_control_msgs__srv__SetOperationalMode_Request__Sequence * array, size_t size);

/// Finalize array of srv/SetOperationalMode messages.
/**
 * It calls
 * rover_control_msgs__srv__SetOperationalMode_Request__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
void
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__fini(rover_control_msgs__srv__SetOperationalMode_Request__Sequence * array);

/// Create array of srv/SetOperationalMode messages.
/**
 * It allocates the memory for the array and calls
 * rover_control_msgs__srv__SetOperationalMode_Request__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
rover_control_msgs__srv__SetOperationalMode_Request__Sequence *
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__create(size_t size);

/// Destroy array of srv/SetOperationalMode messages.
/**
 * It calls
 * rover_control_msgs__srv__SetOperationalMode_Request__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
void
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__destroy(rover_control_msgs__srv__SetOperationalMode_Request__Sequence * array);

/// Check for srv/SetOperationalMode message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__are_equal(const rover_control_msgs__srv__SetOperationalMode_Request__Sequence * lhs, const rover_control_msgs__srv__SetOperationalMode_Request__Sequence * rhs);

/// Copy an array of srv/SetOperationalMode messages.
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
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Request__Sequence__copy(
  const rover_control_msgs__srv__SetOperationalMode_Request__Sequence * input,
  rover_control_msgs__srv__SetOperationalMode_Request__Sequence * output);

/// Initialize srv/SetOperationalMode message.
/**
 * If the init function is called twice for the same message without
 * calling fini inbetween previously allocated memory will be leaked.
 * \param[in,out] msg The previously allocated message pointer.
 * Fields without a default value will not be initialized by this function.
 * You might want to call memset(msg, 0, sizeof(
 * rover_control_msgs__srv__SetOperationalMode_Response
 * )) before or use
 * rover_control_msgs__srv__SetOperationalMode_Response__create()
 * to allocate and initialize the message.
 * \return true if initialization was successful, otherwise false
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Response__init(rover_control_msgs__srv__SetOperationalMode_Response * msg);

/// Finalize srv/SetOperationalMode message.
/**
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
void
rover_control_msgs__srv__SetOperationalMode_Response__fini(rover_control_msgs__srv__SetOperationalMode_Response * msg);

/// Create srv/SetOperationalMode message.
/**
 * It allocates the memory for the message, sets the memory to zero, and
 * calls
 * rover_control_msgs__srv__SetOperationalMode_Response__init().
 * \return The pointer to the initialized message if successful,
 * otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
rover_control_msgs__srv__SetOperationalMode_Response *
rover_control_msgs__srv__SetOperationalMode_Response__create();

/// Destroy srv/SetOperationalMode message.
/**
 * It calls
 * rover_control_msgs__srv__SetOperationalMode_Response__fini()
 * and frees the memory of the message.
 * \param[in,out] msg The allocated message pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
void
rover_control_msgs__srv__SetOperationalMode_Response__destroy(rover_control_msgs__srv__SetOperationalMode_Response * msg);

/// Check for srv/SetOperationalMode message equality.
/**
 * \param[in] lhs The message on the left hand size of the equality operator.
 * \param[in] rhs The message on the right hand size of the equality operator.
 * \return true if messages are equal, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Response__are_equal(const rover_control_msgs__srv__SetOperationalMode_Response * lhs, const rover_control_msgs__srv__SetOperationalMode_Response * rhs);

/// Copy a srv/SetOperationalMode message.
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
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Response__copy(
  const rover_control_msgs__srv__SetOperationalMode_Response * input,
  rover_control_msgs__srv__SetOperationalMode_Response * output);

/// Initialize array of srv/SetOperationalMode messages.
/**
 * It allocates the memory for the number of elements and calls
 * rover_control_msgs__srv__SetOperationalMode_Response__init()
 * for each element of the array.
 * \param[in,out] array The allocated array pointer.
 * \param[in] size The size / capacity of the array.
 * \return true if initialization was successful, otherwise false
 * If the array pointer is valid and the size is zero it is guaranteed
 # to return true.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__init(rover_control_msgs__srv__SetOperationalMode_Response__Sequence * array, size_t size);

/// Finalize array of srv/SetOperationalMode messages.
/**
 * It calls
 * rover_control_msgs__srv__SetOperationalMode_Response__fini()
 * for each element of the array and frees the memory for the number of
 * elements.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
void
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__fini(rover_control_msgs__srv__SetOperationalMode_Response__Sequence * array);

/// Create array of srv/SetOperationalMode messages.
/**
 * It allocates the memory for the array and calls
 * rover_control_msgs__srv__SetOperationalMode_Response__Sequence__init().
 * \param[in] size The size / capacity of the array.
 * \return The pointer to the initialized array if successful, otherwise NULL
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
rover_control_msgs__srv__SetOperationalMode_Response__Sequence *
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__create(size_t size);

/// Destroy array of srv/SetOperationalMode messages.
/**
 * It calls
 * rover_control_msgs__srv__SetOperationalMode_Response__Sequence__fini()
 * on the array,
 * and frees the memory of the array.
 * \param[in,out] array The initialized array pointer.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
void
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__destroy(rover_control_msgs__srv__SetOperationalMode_Response__Sequence * array);

/// Check for srv/SetOperationalMode message array equality.
/**
 * \param[in] lhs The message array on the left hand size of the equality operator.
 * \param[in] rhs The message array on the right hand size of the equality operator.
 * \return true if message arrays are equal in size and content, otherwise false.
 */
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__are_equal(const rover_control_msgs__srv__SetOperationalMode_Response__Sequence * lhs, const rover_control_msgs__srv__SetOperationalMode_Response__Sequence * rhs);

/// Copy an array of srv/SetOperationalMode messages.
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
ROSIDL_GENERATOR_C_PUBLIC_rover_control_msgs
bool
rover_control_msgs__srv__SetOperationalMode_Response__Sequence__copy(
  const rover_control_msgs__srv__SetOperationalMode_Response__Sequence * input,
  rover_control_msgs__srv__SetOperationalMode_Response__Sequence * output);

#ifdef __cplusplus
}
#endif

#endif  // ROVER_CONTROL_MSGS__SRV__DETAIL__SET_OPERATIONAL_MODE__FUNCTIONS_H_
