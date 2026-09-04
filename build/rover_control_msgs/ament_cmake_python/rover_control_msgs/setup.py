from setuptools import find_packages
from setuptools import setup

setup(
    name='rover_control_msgs',
    version='0.0.0',
    packages=find_packages(
        include=('rover_control_msgs', 'rover_control_msgs.*')),
)
