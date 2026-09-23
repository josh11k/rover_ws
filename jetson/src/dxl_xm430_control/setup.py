import os
from glob import glob
from setuptools import setup

package_name = 'dxl_xm430_control'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='you',
    maintainer_email='you@example.com',
    description='Dynamixel XM430-W350-R Steuerung ueber U2D2',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'xm430_node = dxl_xm430_control.xm430_node:main',
        ],
    },
)
