#!/usr/bin/env bash
set -e

ROS_DISTRO_SETUP="/opt/ros/humble/setup.bash"
WORKSPACE_SETUP="/home/team/rover_2026/rover_ws/jetson/install/setup.bash"
LAUNCH_PACKAGE="rover_perception"
LAUNCH_FILE="stereo_lidar_fusion.launch.py"
LAUNCH_ARGS=""

source "${ROS_DISTRO_SETUP}"
source "${WORKSPACE_SETUP}"

exec ros2 launch "${LAUNCH_PACKAGE}" "${LAUNCH_FILE}" ${LAUNCH_ARGS}

