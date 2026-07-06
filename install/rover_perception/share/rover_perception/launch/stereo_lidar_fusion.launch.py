"""Launch the perception module's fake sensors + processing pipeline.

Wires together (see ARCHITECTURE.md for the full picture):

  fake_lidar_node (rover_lidar)  --\\
                                     >-- frame_transform_node --> pointcloud_preprocessing_node --\\
  fake_stereo_camera_node        --/     (x2, one per sensor)      (x2, one per sensor)             >-- global_pointcloud_fusion_node --> obstacle_grid_node
       |                                                                                          /
       v                                                                                         /
  stereo_pointcloud_node  ---------------------------------------------------------------------/

  fake_mono_camera_node --> led_detector_node --> /mono_cam/led_detections
    (separate branch -- not fed into the point-cloud fusion above;
    position_rover_node, not yet built, is its next consumer)

The whole perception module (this Jetson, with all its sensors) sits on a
~1.2m mast -- it does not move with the rover. `mast_base_link`/
`mast_platform_link` (see below) are therefore the module's own reference
frames, not a vehicle body frame. The rover itself is a separate thing,
tracked externally via the mono-cam LED branch.

The mast's dynamic kinematics (pan at the base, tilt at the platform, mast
lean) are now handled by mast_pose_node, fed by fake_mast_hw_node (pan/tilt
JointState + electronics-box IMU) plus the IMUs fake_stereo_camera_node and
fake_lidar_node already publish:

    world --[lean, from hardware-box IMU]--> mast_base_link
    mast_base_link --[pan+tilt, from JointState]--> mast_platform_link

Everything downstream targets `mast_base_link`, not `mast_platform_link`,
on purpose: the platform pans, so building the terrain grid relative to it
would make the map spin with every pan movement instead of accumulating a
stable view across multiple look directions. `mast_base_link` only moves
under genuine mast lean (quasi-static), which is what we want a "fixed"
map frame to track.

Static TF publishers below provide only the fixed sensor -> mast_platform_
link extrinsics (mechanical mounting offsets, don't change with pan/tilt).
The values are PLACEHOLDERS -- replace them with the actual measured (or
calibrated) mounting pose of the LiDAR, stereo camera and mono camera on
the platform before trusting the fused output.

Note on the stereo/mono camera static transforms: published directly as
mast_platform_link -> camera_depth_optical_frame / mono_cam_optical_frame
and therefore also bake in the REP-103 optical-axis rotation (camera looks
along +Z, X right, Y down) on top of the physical mounting pose. Once the
mechanical design is final, consider splitting each into mast_platform_
link -> camera_link (physical pose) + a fixed camera_link -> *_optical_
frame rotation, which is how realsense2_camera's own URDF/TF tree is
structured -- that split makes it trivial to swap in the real driver later
without recomputing the rotation.
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

    fake_mono = Node(
        package="rover_perception",
        executable="fake_mono_camera_node",
        name="fake_mono_camera_node",
    )

    # Fake pan/tilt motor feedback + electronics-box IMU -- see
    # fake_mast_hw_node.py. Swap for the real motor-controller interface
    # once it exists.
    fake_mast_hw = Node(
        package="rover_perception",
        executable="fake_mast_hw_node",
        name="fake_mast_hw_node",
    )

    # Computes the mast's two dynamic transforms (world->mast_base_link
    # lean, mast_base_link->mast_platform_link pan/tilt) from the above +
    # the stereo/lidar IMUs. See mast_pose_node.py for the full reasoning.
    mast_pose = Node(
        package="rover_perception",
        executable="mast_pose_node",
        name="mast_pose_node",
    )

    # ------------------------------------------------------------------
    # Static extrinsics: sensor frame -> mast_platform_link (fixed
    # mechanical mounts, don't move with pan/tilt). TODO calibrate.
    # ------------------------------------------------------------------
    lidar_static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="lidar_to_mast_platform_link",
        arguments=[
            "--x", "0.0", "--y", "0.0", "--z", "0.60",
            "--roll", "0.0", "--pitch", "0.0", "--yaw", "0.0",
            "--frame-id", "mast_platform_link",
            "--child-frame-id", "lidar_frame",
        ],
    )

    stereo_static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="stereo_to_mast_platform_link",
        arguments=[
            "--x", "0.20", "--y", "0.0", "--z", "0.40",
            # REP-103 optical rotation (camera body forward -> +Z optical)
            # composed with a level (non-tilted) mount. Adjust once the
            # camera's physical tilt on the platform is known.
            "--roll", "-1.5708", "--pitch", "0.0", "--yaw", "-1.5708",
            "--frame-id", "mast_platform_link",
            "--child-frame-id", "camera_depth_optical_frame",
        ],
    )

    mono_static_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        name="mono_to_mast_platform_link",
        arguments=[
            "--x", "0.0", "--y", "0.15", "--z", "0.50",
            # Same REP-103 optical rotation as the stereo camera above --
            # both cameras use the same (Z-forward, X-right, Y-down)
            # convention. Adjust once the mono cam's physical mount pose on
            # the platform is known.
            "--roll", "-1.5708", "--pitch", "0.0", "--yaw", "-1.5708",
            "--frame-id", "mast_platform_link",
            "--child-frame-id", "mono_cam_optical_frame",
        ],
    )

    # ------------------------------------------------------------------
    # Per-sensor: transform to mast_base_link (not mast_platform_link --
    # see module docstring), then filter.
    # ------------------------------------------------------------------
    lidar_transform = Node(
        package="rover_perception",
        executable="frame_transform_node",
        name="lidar_frame_transform_node",
        parameters=[{
            "input_topic": "/livox/points",
            "output_topic": "/lidar/points_mast_base_link",
            "target_frame": "mast_base_link",
        }],
    )

    lidar_preprocessing = Node(
        package="rover_perception",
        executable="pointcloud_preprocessing_node",
        name="lidar_preprocessing_node",
        parameters=[{
            "input_topic": "/lidar/points_mast_base_link",
            "output_topic": "/lidar/points_filtered",
            "voxel_size": 0.20,
            "outlier_radius": 2.0,
            "min_neighbors": 1,
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
            "output_topic": "/stereo/points_mast_base_link",
            "target_frame": "mast_base_link",
        }],
    )

    stereo_preprocessing = Node(
        package="rover_perception",
        executable="pointcloud_preprocessing_node",
        name="stereo_preprocessing_node",
        parameters=[{
            "input_topic": "/stereo/points_mast_base_link",
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

    # ------------------------------------------------------------------
    # Mono-cam / LED branch. Separate from the point-cloud fusion above --
    # its output (/mono_cam/led_detections) has no consumer yet
    # (position_rover_node isn't built).
    # ------------------------------------------------------------------
    led_detector = Node(
        package="rover_perception",
        executable="led_detector_node",
        name="led_detector_node",
    )

    for action in [
        fake_lidar, fake_stereo, fake_mono, fake_mast_hw,
        mast_pose,
        lidar_static_tf, stereo_static_tf, mono_static_tf,
        lidar_transform, lidar_preprocessing,
        stereo_to_cloud, stereo_transform, stereo_preprocessing,
        fusion, obstacle_grid,
        led_detector,
    ]:
        ld.add_action(action)

    return ld
