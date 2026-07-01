"""Launch the stereo + lidar fusion pipeline (fake sensors by default).

Wires together (see ARCHITECTURE.md for the full picture):

  fake_lidar_node (rover_lidar)  --\\
                                     >-- frame_transform_node --> pointcloud_preprocessing_node --\\
  fake_stereo_camera_node        --/     (x2, one per sensor)      (x2, one per sensor)             >-- global_pointcloud_fusion_node --> obstacle_grid_node
       |                                                                                          /
       v                                                                                         /
  stereo_pointcloud_node  ---------------------------------------------------------------------/

Static TF publishers provide the sensor -> base_link extrinsics. The
values below are PLACEHOLDERS -- replace them with the actual measured (or
calibrated) mounting pose of the LiDAR and stereo camera on the perception
module before trusting the fused output.

Note on the stereo camera's static transform: it is published directly as
base_link -> camera_depth_optical_frame and therefore also bakes in the
REP-103 optical-axis rotation (camera looks along +Z, X right, Y down)
on top of the physical mounting pose. Once the mechanical design is final,
consider splitting this into base_link -> camera_link (physical pose) and
a fixed camera_link -> camera_depth_optical_frame rotation, which is how
realsense2_camera's own URDF/TF tree is structured -- that split makes it
trivial to swap in the real driver later without recomputing the rotation.
"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    ld = LaunchDescription()

    # ------------------------------------------------------------------
    # Sensor sources (fakes; swap for the real drivers when hardware is
    # attached -- livox_ros_driver2 for the Mid-360, realsense2_camera for
    # the D400-series stereo camera. Downstream nodes don't need to change
    # since topics/frames/message types already match the real drivers).
    # ------------------------------------------------------------------
    fake_lidar = Node(
        package="rover_lidar",
        executable="fake_lidar_node",
        name="fake_lidar_node",
    )

    fake_stereo = Node(
        package="rover_perception",
        executable="fake_stereo_camera_node",
        name="fake_stereo_camera_node",
    )

    # ------------------------------------------------------------------
    # Static extrinsics: sensor frame -> base_link. TODO calibrate.
    # ------------------------------------------------------------------
    lidar_static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="lidar_to_base_link",
        arguments=[
            "--x", "0.0", "--y", "0.0", "--z", "0.60",
            "--roll", "0.0", "--pitch", "0.0", "--yaw", "0.0",
            "--frame-id", "base_link",
            "--child-frame-id", "lidar_frame",
        ],
    )

    stereo_static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="stereo_to_base_link",
        arguments=[
            "--x", "0.20", "--y", "0.0", "--z", "0.40",
            # REP-103 optical rotation (camera body forward -> +Z optical)
            # composed with a level (non-tilted) mount. Adjust once the
            # camera's physical tilt on the mast/perception box is known.
            "--roll", "-1.5708", "--pitch", "0.0", "--yaw", "-1.5708",
            "--frame-id", "base_link",
            "--child-frame-id", "camera_depth_optical_frame",
        ],
    )

    # ------------------------------------------------------------------
    # Per-sensor: transform to base_link, then filter.
    # ------------------------------------------------------------------
    lidar_transform = Node(
        package="rover_perception",
        executable="frame_transform_node",
        name="lidar_frame_transform_node",
        parameters=[{
            "input_topic": "/livox/points",
            "output_topic": "/lidar/points_base_link",
            "target_frame": "base_link",
        }],
    )

    lidar_preprocessing = Node(
        package="rover_perception",
        executable="pointcloud_preprocessing_node",
        name="lidar_preprocessing_node",
        parameters=[{
            "input_topic": "/lidar/points_base_link",
            "output_topic": "/lidar/points_filtered",
            "voxel_size": 0.20,
            "outlier_radius": 0.50,
            "min_neighbors": 2,
        }],
    )

    stereo_to_cloud = Node(
        package="rover_perception",
        executable="stereo_pointcloud_node",
        name="stereo_pointcloud_node",
    )

    stereo_transform = Node(
        package="rover_perception",
        executable="frame_transform_node",
        name="stereo_frame_transform_node",
        parameters=[{
            "input_topic": "/stereo/points",
            "output_topic": "/stereo/points_base_link",
            "target_frame": "base_link",
        }],
    )

    stereo_preprocessing = Node(
        package="rover_perception",
        executable="pointcloud_preprocessing_node",
        name="stereo_preprocessing_node",
        parameters=[{
            "input_topic": "/stereo/points_base_link",
            "output_topic": "/stereo/points_filtered",
            "voxel_size": 0.10,
            "outlier_radius": 0.30,
            "min_neighbors": 3,
        }],
    )

    # ------------------------------------------------------------------
    # Fusion + terrain analysis.
    # ------------------------------------------------------------------
    fusion = Node(
        package="rover_perception",
        executable="global_pointcloud_fusion_node",
        name="global_pointcloud_fusion_node",
        parameters=[{
            "lidar_points_topic": "/lidar/points_filtered",
            "stereo_points_topic": "/stereo/points_filtered",
            "output_topic": "/perception/global_points",
        }],
    )

    obstacle_grid = Node(
        package="rover_perception",
        executable="obstacle_grid_node",
        name="obstacle_grid_node",
        parameters=[{
            "points_topic": "/perception/global_points",
        }],
    )

    for action in [
        fake_lidar, fake_stereo,
        lidar_static_tf, stereo_static_tf,
        lidar_transform, lidar_preprocessing,
        stereo_to_cloud, stereo_transform, stereo_preprocessing,
        fusion, obstacle_grid,
    ]:
        ld.add_action(action)

    return ld
