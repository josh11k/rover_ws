"""Fake stand-in for the two mast-hardware inputs that don't have a home in
any other fake node yet: the electronics-box IMU, and the pan/tilt motor
controller's joint-state feedback.

Unlike fake_stereo_camera_node's IMU or fake_lidar_node's IMU (which mirror
a specific real sensor's own driver output), there's no existing hardware
interface these two are copying -- the electronics box has no driver yet,
and the pan/tilt motor controller's ROS2 interface doesn't exist yet
either. So this node's topics/message layout are the current best guess
(sensor_msgs/Imu, sensor_msgs/JointState -- both already-standard message
types, see mast_pose_node.py) rather than a copy of a real driver's output.
When the real hardware interface is built, only the topic names likely need
to line up (or get remapped) -- both message types are already correct.

Simulates a mast that's very slightly off-level (fixed small lean, doesn't
move -- see FakeUsbInterface-style hardware stubs elsewhere for why this
stays intentionally simple) and a platform that slowly pans back and forth
and tilts, so mast_pose_node has non-trivial, changing joint angles to
publish as TF while no real motor controller exists.
"""

import math

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Imu, JointState


DEFAULTS = {
    "hardware_box_imu_topic": "/hardware_box/imu",
    "joint_state_topic": "/mast/joint_states",
    "frame_id": "hardware_box_link",

    "publish_rate_hz": 10.0,

    # Fixed, small simulated mast lean (degrees) -- e.g. the mast isn't
    # perfectly plumb. Doesn't change over time; real mast lean would drift
    # slowly (wind, ground settling), not oscillate like pan/tilt below.
    "fake_lean_deg": 1.5,

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

        self.imu_pub = self.create_publisher(
            Imu, self.hardware_box_imu_topic, qos_profile_sensor_data,
        )
        self.joint_state_pub = self.create_publisher(
            JointState, self.joint_state_topic, 10,
        )

        self._start_time = self.get_clock().now()

        # Fixed lean quaternion, precomputed once (doesn't change per
        # frame): a pure pitch of fake_lean_deg.
        half_angle = math.radians(self.fake_lean_deg) / 2.0
        self._lean_qy = math.sin(half_angle)
        self._lean_qw = math.cos(half_angle)

        period = 1.0 / self.publish_rate_hz
        self.timer = self.create_timer(period, self.timer_callback)

        self.get_logger().info(
            f"fake_mast_hw_node: {self.hardware_box_imu_topic} "
            f"(fixed {self.fake_lean_deg} deg lean) + "
            f"{self.joint_state_topic} (pan +/-{self.pan_amplitude_deg} deg, "
            f"tilt +/-{self.tilt_amplitude_deg} deg)"
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

        imu_msg = Imu()
        imu_msg.header.stamp = stamp
        imu_msg.header.frame_id = self.frame_id
        imu_msg.orientation.y = self._lean_qy
        imu_msg.orientation.w = self._lean_qw
        imu_msg.orientation_covariance = [
            0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01,
        ]
        imu_msg.linear_acceleration.z = 9.81
        self.imu_pub.publish(imu_msg)

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
