from setuptools import find_packages
from setuptools import setup

setup(
    name='rover_perception_msgs',
    version='0.0.0',
    packages=find_packages(
        include=('rover_perception_msgs', 'rover_perception_msgs.*')),
)
