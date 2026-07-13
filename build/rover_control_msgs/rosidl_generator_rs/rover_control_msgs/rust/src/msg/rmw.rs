#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "rover_control_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rover_control_msgs__msg__SetOperationalMode() -> *const std::ffi::c_void;
}

#[link(name = "rover_control_msgs__rosidl_generator_c")]
extern "C" {
    fn rover_control_msgs__msg__SetOperationalMode__init(msg: *mut SetOperationalMode) -> bool;
    fn rover_control_msgs__msg__SetOperationalMode__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<SetOperationalMode>, size: usize) -> bool;
    fn rover_control_msgs__msg__SetOperationalMode__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<SetOperationalMode>);
    fn rover_control_msgs__msg__SetOperationalMode__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<SetOperationalMode>, out_seq: *mut rosidl_runtime_rs::Sequence<SetOperationalMode>) -> bool;
}

// Corresponds to rover_control_msgs__msg__SetOperationalMode
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetOperationalMode {

    // This member is not documented.
    #[allow(missing_docs)]
    pub mode: rosidl_runtime_rs::String,

}



impl Default for SetOperationalMode {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rover_control_msgs__msg__SetOperationalMode__init(&mut msg as *mut _) {
        panic!("Call to rover_control_msgs__msg__SetOperationalMode__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for SetOperationalMode {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__msg__SetOperationalMode__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__msg__SetOperationalMode__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__msg__SetOperationalMode__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for SetOperationalMode {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for SetOperationalMode where Self: Sized {
  const TYPE_NAME: &'static str = "rover_control_msgs/msg/SetOperationalMode";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rover_control_msgs__msg__SetOperationalMode() }
  }
}


#[link(name = "rover_control_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rover_control_msgs__msg__OperationalModeSettings() -> *const std::ffi::c_void;
}

#[link(name = "rover_control_msgs__rosidl_generator_c")]
extern "C" {
    fn rover_control_msgs__msg__OperationalModeSettings__init(msg: *mut OperationalModeSettings) -> bool;
    fn rover_control_msgs__msg__OperationalModeSettings__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<OperationalModeSettings>, size: usize) -> bool;
    fn rover_control_msgs__msg__OperationalModeSettings__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<OperationalModeSettings>);
    fn rover_control_msgs__msg__OperationalModeSettings__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<OperationalModeSettings>, out_seq: *mut rosidl_runtime_rs::Sequence<OperationalModeSettings>) -> bool;
}

// Corresponds to rover_control_msgs__msg__OperationalModeSettings
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct OperationalModeSettings {

    // This member is not documented.
    #[allow(missing_docs)]
    pub stereo_cam: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mono_cam: rosidl_runtime_rs::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lidar: rosidl_runtime_rs::String,

}



impl Default for OperationalModeSettings {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rover_control_msgs__msg__OperationalModeSettings__init(&mut msg as *mut _) {
        panic!("Call to rover_control_msgs__msg__OperationalModeSettings__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for OperationalModeSettings {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__msg__OperationalModeSettings__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__msg__OperationalModeSettings__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__msg__OperationalModeSettings__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for OperationalModeSettings {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for OperationalModeSettings where Self: Sized {
  const TYPE_NAME: &'static str = "rover_control_msgs/msg/OperationalModeSettings";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rover_control_msgs__msg__OperationalModeSettings() }
  }
}


#[link(name = "rover_control_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rover_control_msgs__msg__CurrentOperationalMode() -> *const std::ffi::c_void;
}

#[link(name = "rover_control_msgs__rosidl_generator_c")]
extern "C" {
    fn rover_control_msgs__msg__CurrentOperationalMode__init(msg: *mut CurrentOperationalMode) -> bool;
    fn rover_control_msgs__msg__CurrentOperationalMode__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<CurrentOperationalMode>, size: usize) -> bool;
    fn rover_control_msgs__msg__CurrentOperationalMode__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<CurrentOperationalMode>);
    fn rover_control_msgs__msg__CurrentOperationalMode__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<CurrentOperationalMode>, out_seq: *mut rosidl_runtime_rs::Sequence<CurrentOperationalMode>) -> bool;
}

// Corresponds to rover_control_msgs__msg__CurrentOperationalMode
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CurrentOperationalMode {

    // This member is not documented.
    #[allow(missing_docs)]
    pub mode: rosidl_runtime_rs::String,

}



impl Default for CurrentOperationalMode {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rover_control_msgs__msg__CurrentOperationalMode__init(&mut msg as *mut _) {
        panic!("Call to rover_control_msgs__msg__CurrentOperationalMode__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for CurrentOperationalMode {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__msg__CurrentOperationalMode__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__msg__CurrentOperationalMode__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_control_msgs__msg__CurrentOperationalMode__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for CurrentOperationalMode {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for CurrentOperationalMode where Self: Sized {
  const TYPE_NAME: &'static str = "rover_control_msgs/msg/CurrentOperationalMode";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rover_control_msgs__msg__CurrentOperationalMode() }
  }
}


