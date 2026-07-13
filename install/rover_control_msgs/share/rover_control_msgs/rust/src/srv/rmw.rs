#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



#[link(name = "rover_control_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rover_control_msgs__srv__SetOperationalMode_Request() -> *const std::ffi::c_void;
}

#[link(name = "rover_control_msgs__rosidl_generator_c")]
extern "C" {
    fn rover_control_msgs__srv__SetOperationalMode_Request__init(msg: *mut SetOperationalMode_Request) -> bool;
    fn rover_control_msgs__srv__SetOperationalMode_Request__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<SetOperationalMode_Request>, size: usize) -> bool;
    fn rover_control_msgs__srv__SetOperationalMode_Request__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<SetOperationalMode_Request>);
    fn rover_control_msgs__srv__SetOperationalMode_Request__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<SetOperationalMode_Request>, out_seq: *mut rosidl_runtime_rs::Sequence<SetOperationalMode_Request>) -> bool;
}

// Corresponds to rover_control_msgs__srv__SetOperationalMode_Request
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetOperationalMode_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub mode: rosidl_runtime_rs::String,

}



impl Default for SetOperationalMode_Request {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rover_control_msgs__srv__SetOperationalMode_Request__init(&mut msg as *mut _) {
        panic!("Call to rover_control_msgs__srv__SetOperationalMode_Request__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for SetOperationalMode_Request {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__srv__SetOperationalMode_Request__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__srv__SetOperationalMode_Request__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__srv__SetOperationalMode_Request__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for SetOperationalMode_Request {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for SetOperationalMode_Request where Self: Sized {
  const TYPE_NAME: &'static str = "rover_control_msgs/srv/SetOperationalMode_Request";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rover_control_msgs__srv__SetOperationalMode_Request() }
  }
}


#[link(name = "rover_control_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rover_control_msgs__srv__SetOperationalMode_Response() -> *const std::ffi::c_void;
}

#[link(name = "rover_control_msgs__rosidl_generator_c")]
extern "C" {
    fn rover_control_msgs__srv__SetOperationalMode_Response__init(msg: *mut SetOperationalMode_Response) -> bool;
    fn rover_control_msgs__srv__SetOperationalMode_Response__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<SetOperationalMode_Response>, size: usize) -> bool;
    fn rover_control_msgs__srv__SetOperationalMode_Response__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<SetOperationalMode_Response>);
    fn rover_control_msgs__srv__SetOperationalMode_Response__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<SetOperationalMode_Response>, out_seq: *mut rosidl_runtime_rs::Sequence<SetOperationalMode_Response>) -> bool;
}

// Corresponds to rover_control_msgs__srv__SetOperationalMode_Response
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetOperationalMode_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: rosidl_runtime_rs::String,

}



impl Default for SetOperationalMode_Response {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rover_control_msgs__srv__SetOperationalMode_Response__init(&mut msg as *mut _) {
        panic!("Call to rover_control_msgs__srv__SetOperationalMode_Response__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for SetOperationalMode_Response {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__srv__SetOperationalMode_Response__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__srv__SetOperationalMode_Response__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__srv__SetOperationalMode_Response__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for SetOperationalMode_Response {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for SetOperationalMode_Response where Self: Sized {
  const TYPE_NAME: &'static str = "rover_control_msgs/srv/SetOperationalMode_Response";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rover_control_msgs__srv__SetOperationalMode_Response() }
  }
}






#[link(name = "rover_control_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_service_type_support_handle__rover_control_msgs__srv__SetOperationalMode() -> *const std::ffi::c_void;
}

// Corresponds to rover_control_msgs__srv__SetOperationalMode
#[allow(missing_docs, non_camel_case_types)]
pub struct SetOperationalMode;

impl rosidl_runtime_rs::Service for SetOperationalMode {
    type Request = SetOperationalMode_Request;
    type Response = SetOperationalMode_Response;

    fn get_type_support() -> *const std::ffi::c_void {
        // SAFETY: No preconditions for this function.
        unsafe { rosidl_typesupport_c__get_service_type_support_handle__rover_control_msgs__srv__SetOperationalMode() }
    }
}


