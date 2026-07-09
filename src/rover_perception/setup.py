from setuptools import find_packages, setup

package_name = 'rover_perception'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', [
            'launch/stereo_lidar_fusion.launch.py',
        ]),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='joshua',
    maintainer_email='joshua.kaelble@gmx.dem',
    description='Perception stack: mono/stereo/lidar/IMU fusion for the Jetson perception module.',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'fake_stereo_camera_node = rover_perception.fake_stereo_camera_node:main',
            'stereo_pointcloud_node = rover_perception.stereo_pointcloud_node:main',
            'frame_transform_node = rover_perception.frame_transform_node:main',
            'pointcloud_preprocessing_node = rover_perception.pointcloud_preprocessing_node:main',
            'global_pointcloud_fusion_node = rover_perception.global_pointcloud_fusion_node:main',
            'obstacle_grid_node = rover_perception.obstacle_grid_node:main',
            'fake_mono_camera_node = rover_perception.fake_mono_camera_node:main',
            'led_detector_node = rover_perception.led_detector_node:main',
            'mast_pose_node = rover_perception.mast_pose_node:main',
            'fake_mast_hw_node = rover_perception.fake_mast_hw_node:main',
            'terrain_visualization_node = rover_perception.terrain_visualization_node:main',
            'position_rover_node = rover_perception.position_rover_node:main',
        ],
    },
)
