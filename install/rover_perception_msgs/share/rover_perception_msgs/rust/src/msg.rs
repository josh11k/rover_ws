#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to rover_perception_msgs__msg__TerrainGrid
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

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct TerrainGrid {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub info: nav_msgs::msg::MapMetaData,

    /// same values/semantics as OccupancyGrid.data
    pub traversability: Vec<i8>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub min_z: Vec<f32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub max_z: Vec<f32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub mean_z: Vec<f32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub roughness: Vec<f32>,


    // This member is not documented.
    #[allow(missing_docs)]
    pub plane_slope_deg: Vec<f32>,

    /// raw number of points that fell in the cell
    pub point_count: Vec<i32>,

    /// sum of per-point weight/confidence in the
    /// cell -- this (not point_count) is what gates
    /// whether a cell counts as "known" terrain,
    /// see rover_perception/terrain_analysis.py
    pub total_weight: Vec<f32>,

}



impl Default for TerrainGrid {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::TerrainGrid::default())
  }
}

impl rosidl_runtime_rs::Message for TerrainGrid {
  type RmwMsg = super::msg::rmw::TerrainGrid;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        info: nav_msgs::msg::MapMetaData::into_rmw_message(std::borrow::Cow::Owned(msg.info)).into_owned(),
        traversability: msg.traversability.into(),
        min_z: msg.min_z.into(),
        max_z: msg.max_z.into(),
        mean_z: msg.mean_z.into(),
        roughness: msg.roughness.into(),
        plane_slope_deg: msg.plane_slope_deg.into(),
        point_count: msg.point_count.into(),
        total_weight: msg.total_weight.into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        info: nav_msgs::msg::MapMetaData::into_rmw_message(std::borrow::Cow::Borrowed(&msg.info)).into_owned(),
        traversability: msg.traversability.as_slice().into(),
        min_z: msg.min_z.as_slice().into(),
        max_z: msg.max_z.as_slice().into(),
        mean_z: msg.mean_z.as_slice().into(),
        roughness: msg.roughness.as_slice().into(),
        plane_slope_deg: msg.plane_slope_deg.as_slice().into(),
        point_count: msg.point_count.as_slice().into(),
        total_weight: msg.total_weight.as_slice().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      info: nav_msgs::msg::MapMetaData::from_rmw_message(msg.info),
      traversability: msg.traversability
          .into_iter()
          .collect(),
      min_z: msg.min_z
          .into_iter()
          .collect(),
      max_z: msg.max_z
          .into_iter()
          .collect(),
      mean_z: msg.mean_z
          .into_iter()
          .collect(),
      roughness: msg.roughness
          .into_iter()
          .collect(),
      plane_slope_deg: msg.plane_slope_deg
          .into_iter()
          .collect(),
      point_count: msg.point_count
          .into_iter()
          .collect(),
      total_weight: msg.total_weight
          .into_iter()
          .collect(),
    }
  }
}


// Corresponds to rover_perception_msgs__msg__LedDetection
/// A single LED blob detected in a mono-camera image by led_detector_node.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
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
    pub bearing: geometry_msgs::msg::Vector3,

}



impl Default for LedDetection {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::LedDetection::default())
  }
}

impl rosidl_runtime_rs::Message for LedDetection {
  type RmwMsg = super::msg::rmw::LedDetection;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        pixel_u: msg.pixel_u,
        pixel_v: msg.pixel_v,
        area_px: msg.area_px,
        color_r: msg.color_r,
        color_g: msg.color_g,
        color_b: msg.color_b,
        bearing: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.bearing)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      pixel_u: msg.pixel_u,
      pixel_v: msg.pixel_v,
      area_px: msg.area_px,
      color_r: msg.color_r,
      color_g: msg.color_g,
      color_b: msg.color_b,
        bearing: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.bearing)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      pixel_u: msg.pixel_u,
      pixel_v: msg.pixel_v,
      area_px: msg.area_px,
      color_r: msg.color_r,
      color_g: msg.color_g,
      color_b: msg.color_b,
      bearing: geometry_msgs::msg::Vector3::from_rmw_message(msg.bearing),
    }
  }
}


// Corresponds to rover_perception_msgs__msg__LedDetectionArray
/// All LED blobs detected in one mono-camera frame.
///
/// header.stamp/frame_id are copied from the source image (frame_id =
/// mono_cam_optical_frame), so detections can be time- and frame-correlated
/// with everything else in the pipeline. Empty `detections` is a normal,
/// valid message (no LEDs visible this frame) -- not an error condition.

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct LedDetectionArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub detections: Vec<super::msg::LedDetection>,

}



impl Default for LedDetectionArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::LedDetectionArray::default())
  }
}

impl rosidl_runtime_rs::Message for LedDetectionArray {
  type RmwMsg = super::msg::rmw::LedDetectionArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        detections: msg.detections
          .into_iter()
          .map(|elem| super::msg::LedDetection::into_rmw_message(std::borrow::Cow::Owned(elem)).into_owned())
          .collect(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        detections: msg.detections
          .iter()
          .map(|elem| super::msg::LedDetection::into_rmw_message(std::borrow::Cow::Borrowed(elem)).into_owned())
          .collect(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      detections: msg.detections
          .into_iter()
          .map(super::msg::LedDetection::from_rmw_message)
          .collect(),
    }
  }
}


