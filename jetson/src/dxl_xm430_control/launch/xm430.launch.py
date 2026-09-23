import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('dxl_xm430_control'), 'config', 'xm430.yaml')

    return LaunchDescription([
        Node(
            package='dxl_xm430_control',
            executable='xm430_node',
            name='xm430_node',
            output='screen',
            parameters=[config],
        ),
    ])
