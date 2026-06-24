from setuptools import find_packages, setup

package_name = 'rover_lidar'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='joshua',
    maintainer_email='joshua.kaelble@gmx.dem',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'fake_lidar_node = rover_lidar.fake_lidar_node:main',
            'lidar_processing_node = rover_lidar.lidar_processing_node:main',
        ],
    },
)
