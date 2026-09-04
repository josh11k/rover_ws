#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};




// Corresponds to rover_control_msgs__srv__SetOperationalMode_Request

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetOperationalMode_Request {

    // This member is not documented.
    #[allow(missing_docs)]
    pub mode: std::string::String,

}



impl Default for SetOperationalMode_Request {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::SetOperationalMode_Request::default())
  }
}

impl rosidl_runtime_rs::Message for SetOperationalMode_Request {
  type RmwMsg = super::srv::rmw::SetOperationalMode_Request;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        mode: msg.mode.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        mode: msg.mode.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      mode: msg.mode.to_string(),
    }
  }
}


// Corresponds to rover_control_msgs__srv__SetOperationalMode_Response

// This struct is not documented.
#[allow(missing_docs)]

#[allow(non_camel_case_types)]
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetOperationalMode_Response {

    // This member is not documented.
    #[allow(missing_docs)]
    pub success: bool,


    // This member is not documented.
    #[allow(missing_docs)]
    pub message: std::string::String,

}



impl Default for SetOperationalMode_Response {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::srv::rmw::SetOperationalMode_Response::default())
  }
}

impl rosidl_runtime_rs::Message for SetOperationalMode_Response {
  type RmwMsg = super::srv::rmw::SetOperationalMode_Response;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        success: msg.success,
        message: msg.message.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      success: msg.success,
        message: msg.message.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      success: msg.success,
      message: msg.message.to_string(),
    }
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


