"""Fake stand-in for the mast-hardware input that doesn't have a home in any
other fake node yet: the pan/tilt motor controller's joint-state feedback.

There's no existing hardware interface to copy here -- the pan/tilt motor
controller's ROS2 interface doesn't exist yet. So this node's topic/message
layout is the current best guess (sensor_msgs/JointState -- already a
standard message type, see mast_pose_node.py) rather than a copy of a real
driver's output. When the real hardware interface is built, only the topic
name likely needs to line up (or get remapped).

Note: this node used to also fake the electronics-box IMU
(/hardware_box/imu). That's now a real sensor -- see imu_icm20649_node.py
(Adafruit ICM-20649 over I2C) -- so there's no fake IMU here anymore. If the
real IMU isn't plugged in, mast_pose_node just has no hardware-box IMU data
at all and falls back to publishing a level (identity-rotation) mast_base
transform rather than a fake lean; see mast_pose_node's
_publish_base_transform.

Simulates a platform that slowly pans back and forth and tilts, so
mast_pose_node has non-trivial, changing joint angles to publish as TF
while no real motor controller exists.
"""

import math

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import JointState


DEFAULTS = {
    "joint_state_topic": "/mast/joint_states",

    "publish_rate_hz": 10.0,

    "pan_joint_name": "mast_pan_joint",
    "tilt_joint_name": "platform_tilt_joint",

    # Slow back-and-forth pan/tilt motion, so mast_pose_node's published TF
    # actually changes over time instead of sitting at a fixed test pose.
    "pan_amplitude_deg": 45.0,
    "pan_period_s": 30.0,
    "tilt_amplitude_deg": 15.0,
    "tilt_period_s": 22.0,
}


class FakeMastHwNode(Node):

    def __init__(self):
        super().__init__("fake_mast_hw_node")

        self._declare_parameters()
        self._load_parameters()

        self.joint_state_pub = self.create_publisher(
            JointState, self.joint_state_topic, 10,
        )

        self._start_time = self.get_clock().now()

        period = 1.0 / self.publish_rate_hz
        self.timer = self.create_timer(period, self.timer_callback)

        self.get_logger().info(
            f"fake_mast_hw_node: {self.joint_state_topic} "
            f"(pan +/-{self.pan_amplitude_deg} deg, "
            f"tilt +/-{self.tilt_amplitude_deg} deg) -- no fake IMU anymore, "
            "see imu_icm20649_node for the real hardware-box IMU"
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def timer_callback(self):
        stamp = self.get_clock().now().to_msg()
        elapsed = (self.get_clock().now() - self._start_time).nanoseconds * 1e-9

        pan_rad = math.radians(self.pan_amplitude_deg) * math.sin(
            2.0 * math.pi * elapsed / max(self.pan_period_s, 1e-3)
        )
        tilt_rad = math.radians(self.tilt_amplitude_deg) * math.sin(
            2.0 * math.pi * elapsed / max(self.tilt_period_s, 1e-3)
        )

        joint_msg = JointState()
        joint_msg.header.stamp = stamp
        joint_msg.name = [self.pan_joint_name, self.tilt_joint_name]
        joint_msg.position = [pan_rad, tilt_rad]
        self.joint_state_pub.publish(joint_msg)


def main(args=None):
    rclpy.init(args=args)

    node = FakeMastHwNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
