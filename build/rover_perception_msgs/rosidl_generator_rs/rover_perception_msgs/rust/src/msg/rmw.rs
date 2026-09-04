#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "rover_perception_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rover_perception_msgs__msg__TerrainGrid() -> *const std::ffi::c_void;
}

#[link(name = "rover_perception_msgs__rosidl_generator_c")]
extern "C" {
    fn rover_perception_msgs__msg__TerrainGrid__init(msg: *mut TerrainGrid) -> bool;
    fn rover_perception_msgs__msg__TerrainGrid__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<TerrainGrid>, size: usize) -> bool;
    fn rover_perception_msgs__msg__TerrainGrid__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<TerrainGrid>);
    fn rover_perception_msgs__msg__TerrainGrid__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<TerrainGrid>, out_seq: *mut rosidl_runtime_rs::Sequence<TerrainGrid>) -> bool;
}

// Corresponds to rover_perception_msgs__msg__TerrainGrid
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// Per-cell terrain statistics, published alongside the collapsed
/// traversability cost already available on nav_msgs/OccupancyGrid
/// (rover_perception's /terrain/traversability_grid).
///
/// Same grid layout as that OccupancyGrid: row-major, index = iy * width + ix,
/// same `info` (resolution/width/height/origin), so cells line up 1:1 and can
/// be correlated by index between the two topics.
///
/// Cells with less than `min_points_per_cell` *effective* points (see
/// total_weight below) use NaN for every float field and 0 for point_count /
/// total_weight -- this mirrors the OccupancyGrid's -1 ("unknown") convention
/// for that same cell, but with a per-field "no data" marker instead of one
/// shared sentinel value, since these are continuous quantities rather than a
/// bounded 0-100 cost.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TerrainGrid {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub info: nav_msgs::msg::rmw::MapMetaData,

    /// same values/semantics as OccupancyGrid.data
    pub traversability: rosidl_runtime_rs::Sequence<i8>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub min_z: rosidl_runtime_rs::Sequence<f32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub max_z: rosidl_runtime_rs::Sequence<f32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mean_z: rosidl_runtime_rs::Sequence<f32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub roughness: rosidl_runtime_rs::Sequence<f32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub plane_slope_deg: rosidl_runtime_rs::Sequence<f32>,

    /// raw number of points that fell in the cell
    pub point_count: rosidl_runtime_rs::Sequence<i32>,

    /// sum of per-point weight/confidence in the
    /// cell -- this (not point_count) is what gates
    /// whether a cell counts as "known" terrain,
    /// see rover_perception/terrain_analysis.py
    pub total_weight: rosidl_runtime_rs::Sequence<f32>,

}



impl Default for TerrainGrid {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rover_perception_msgs__msg__TerrainGrid__init(&mut msg as *mut _) {
        panic!("Call to rover_perception_msgs__msg__TerrainGrid__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for TerrainGrid {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_perception_msgs__msg__TerrainGrid__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_perception_msgs__msg__TerrainGrid__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_perception_msgs__msg__TerrainGrid__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for TerrainGrid {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for TerrainGrid where Self: Sized {
  const TYPE_NAME: &'static str = "rover_perception_msgs/msg/TerrainGrid";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rover_perception_msgs__msg__TerrainGrid() }
  }
}


#[link(name = "rover_perception_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rover_perception_msgs__msg__LedDetection() -> *const std::ffi::c_void;
}

#[link(name = "rover_perception_msgs__rosidl_generator_c")]
extern "C" {
    fn rover_perception_msgs__msg__LedDetection__init(msg: *mut LedDetection) -> bool;
    fn rover_perception_msgs__msg__LedDetection__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<LedDetection>, size: usize) -> bool;
    fn rover_perception_msgs__msg__LedDetection__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<LedDetection>);
    fn rover_perception_msgs__msg__LedDetection__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<LedDetection>, out_seq: *mut rosidl_runtime_rs::Sequence<LedDetection>) -> bool;
}

// Corresponds to rover_perception_msgs__msg__LedDetection
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// A single LED blob detected in a mono-camera image by led_detector_node.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct LedDetection {
    /// blob centroid, image x (pixels)
    pub pixel_u: f32,

    /// blob centroid, image y (pixels)
    pub pixel_v: f32,

    /// blob size, connected-component pixel count
    pub area_px: u32,

    /// mean color of the blob (0-255) -- lets a future
    pub color_r: u8,

    /// consumer match a detection to a known robot's
    pub color_g: u8,

    /// LED color, if robots use distinct colors
    pub color_b: u8,

    /// Unit bearing vector to the blob, in the camera's optical frame (REP-103:
    /// Z forward, X right, Y down). Pre-converted from (pixel_u, pixel_v) via the
    /// camera intrinsics, so downstream nodes can rotate it into base_link with
    /// the same static TF used for the point clouds, without needing pixel
    /// coordinates or intrinsics again. A mono camera alone only gives a
    /// *direction*, not a distance -- turning this into a full 3D position needs
    /// extra information (e.g. known LED spacing, or multi-view triangulation),
    /// which is out of scope for this node.
    pub bearing: geometry_msgs::msg::rmw::Vector3,

}



impl Default for LedDetection {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rover_perception_msgs__msg__LedDetection__init(&mut msg as *mut _) {
        panic!("Call to rover_perception_msgs__msg__LedDetection__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for LedDetection {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_perception_msgs__msg__LedDetection__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_perception_msgs__msg__LedDetection__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_perception_msgs__msg__LedDetection__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for LedDetection {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for LedDetection where Self: Sized {
  const TYPE_NAME: &'static str = "rover_perception_msgs/msg/LedDetection";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rover_perception_msgs__msg__LedDetection() }
  }
}


#[link(name = "rover_perception_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__rover_perception_msgs__msg__LedDetectionArray() -> *const std::ffi::c_void;
}

#[link(name = "rover_perception_msgs__rosidl_generator_c")]
extern "C" {
    fn rover_perception_msgs__msg__LedDetectionArray__init(msg: *mut LedDetectionArray) -> bool;
    fn rover_perception_msgs__msg__LedDetectionArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<LedDetectionArray>, size: usize) -> bool;
    fn rover_perception_msgs__msg__LedDetectionArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<LedDetectionArray>);
    fn rover_perception_msgs__msg__LedDetectionArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<LedDetectionArray>, out_seq: *mut rosidl_runtime_rs::Sequence<LedDetectionArray>) -> bool;
}

// Corresponds to rover_perception_msgs__msg__LedDetectionArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]

/// All LED blobs detected in one mono-camera frame.
///
/// header.stamp/frame_id are copied from the source image (frame_id =
/// mono_cam_optical_frame), so detections can be time- and frame-correlated
/// with everything else in the pipeline. Empty `detections` is a normal,
/// valid message (no LEDs visible this frame) -- not an error condition.

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct LedDetectionArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub detections: rosidl_runtime_rs::Sequence<super::super::msg::rmw::LedDetection>,

}



impl Default for LedDetectionArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !rover_perception_msgs__msg__LedDetectionArray__init(&mut msg as *mut _) {
        panic!("Call to rover_perception_msgs__msg__LedDetectionArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for LedDetectionArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_perception_msgs__msg__LedDetectionArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_perception_msgs__msg__LedDetectionArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { rover_perception_msgs__msg__LedDetectionArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for LedDetectionArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for LedDetectionArray where Self: Sized {
  const TYPE_NAME: &'static str = "rover_perception_msgs/msg/LedDetectionArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__rover_perception_msgs__msg__LedDetectionArray() }
  }
}


