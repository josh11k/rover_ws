#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to rover_control_msgs__msg__SetOperationalMode

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct SetOperationalMode {

    // This member is not documented.
    #[allow(missing_docs)]
    pub mode: std::string::String,

}



impl Default for SetOperationalMode {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::SetOperationalMode::default())
  }
}

impl rosidl_runtime_rs::Message for SetOperationalMode {
  type RmwMsg = super::msg::rmw::SetOperationalMode;

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


// Corresponds to rover_control_msgs__msg__OperationalModeSettings

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct OperationalModeSettings {

    // This member is not documented.
    #[allow(missing_docs)]
    pub stereo_cam: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mono_cam: std::string::String,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lidar: std::string::String,

}



impl Default for OperationalModeSettings {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::OperationalModeSettings::default())
  }
}

impl rosidl_runtime_rs::Message for OperationalModeSettings {
  type RmwMsg = super::msg::rmw::OperationalModeSettings;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stereo_cam: msg.stereo_cam.as_str().into(),
        mono_cam: msg.mono_cam.as_str().into(),
        lidar: msg.lidar.as_str().into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        stereo_cam: msg.stereo_cam.as_str().into(),
        mono_cam: msg.mono_cam.as_str().into(),
        lidar: msg.lidar.as_str().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      stereo_cam: msg.stereo_cam.to_string(),
      mono_cam: msg.mono_cam.to_string(),
      lidar: msg.lidar.to_string(),
    }
  }
}


// Corresponds to rover_control_msgs__msg__CurrentOperationalMode

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct CurrentOperationalMode {

    // This member is not documented.
    #[allow(missing_docs)]
    pub mode: std::string::String,

}



impl Default for CurrentOperationalMode {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::CurrentOperationalMode::default())
  }
}

impl rosidl_runtime_rs::Message for CurrentOperationalMode {
  type RmwMsg = super::msg::rmw::CurrentOperationalMode;

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


