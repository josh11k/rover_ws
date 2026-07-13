"""Compute the mast's dynamic TF chain from motor position + IMUs.

This is the "Int_pose_node" concept from the original diagram, properly
scoped: the perception module sits on a ~1.2m mast that can pan (rotate at
the base) and carries a tiltable platform (lidar/stereo/mono cam mounted
rigidly on it) at its tip. Pan/tilt angle come from motor position; a third
IMU sits in the electronics box further down the mast to catch mast lean.

This node owns exactly the two frames that are genuinely dynamic, and
nothing else -- the sensor-to-platform offsets stay where they already are
(static_transform_publisher in the launch file), because they're fixed by
mechanical design, not something a motor or IMU reports:

    world --[orientation only, from hardware-box IMU]--> mast_base_link
    mast_base_link --[pan+tilt, from JointState]--> mast_platform_link

Output is a normal dynamic TF broadcast (tf2_ros.TransformBroadcaster), not
a custom "pose" message -- frame_transform_node (and anything else using
tf2's lookup_transform) already consumes whatever is in the TF tree, static
or dynamic, without needing to know this node exists. That's the whole
point of using TF2 instead of hand-rolling a pose topic that every consumer
has to subscribe to and transform with manually (see ARCHITECTURE.md for
why that pattern was replaced early on).

Design decisions (see chat history for the reasoning):

- Yaw (pan) is not observable from accelerometer/gyroscope alone (gravity
  doesn't change under pure rotation about the vertical axis) -- so pan
  comes from the motor's JointState only, never "corrected" by an IMU here.
- Tilt (mast lean, platform tilt) IS observable via the gravity vector, but
  the motor encoder is treated as the primary/authoritative source (typic-
  ally low-noise, high-precision) for the actually-published transform.
  The two platform IMUs (stereo + lidar) are used purely as a mutual
  plausibility check -- since they're bolted to the same rigid platform,
  they should report the same orientation; if they disagree beyond
  imu_disagreement_warn_deg, that's logged as a fault/rigidity warning, not
  silently averaged into the transform. A real Kalman-style fusion could
  replace this later once the actual noise characteristics are known.
- world -> mast_base_link's *position* is deliberately left at (0, 0, 0):
  determining the electronics box's actual position is explicitly a later
  task. Only its orientation (lean) is computed here.
- If an IMU's driver already provides a fused orientation quaternion, this
  node uses it directly instead of deriving one from raw accelerometer data
  (per sensor_msgs/Imu convention: orientation_covariance[0] == -1 means
  "orientation not provided", any other value means it's valid).

Placeholder topics (rename via parameters once real drivers exist):
  /hardware_box/imu   -- not built yet
  /camera/imu          -- real realsense2_camera publishes this; fake_stereo_camera_node now fakes it too
  /livox/imu            -- real livox_ros_driver2 publishes this; fake_lidar_node now fakes it too
  /mast/joint_states    -- not built yet (motor controller interface)
"""

import math

import numpy as np
from scipy.spatial.transform import Rotation

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Imu, JointState
from geometry_msgs.msg import TransformStamped

import tf2_ros


DEFAULTS = {
    "hardware_box_imu_topic": "/hardware_box/imu",
    "stereo_imu_topic": "/camera/imu",
    "lidar_imu_topic": "/livox/imu",
    "joint_state_topic": "/mast/joint_states",

    "world_frame": "world",
    "mast_base_frame": "mast_base_link",
    "mast_platform_frame": "mast_platform_link",

    "pan_joint_name": "mast_pan_joint",
    "tilt_joint_name": "platform_tilt_joint",

    # Fixed height of the platform's tilt-joint pivot above mast_base_link,
    # along the (untilted) mast's own Z axis. Placeholder -- replace with
    # the measured mast height.
    "mast_height_m": 1.20,

    # The two platform IMUs (stereo + lidar) should agree closely, since
    # they're bolted to the same rigid platform -- used only as a mutual
    # plausibility check, never fused into the published transform. Warn
    # if they disagree by more than this.
    "imu_disagreement_warn_deg": 5.0,

    "publish_rate_hz": 20.0,
}


def _imu_up_axis(imu_msg: Imu) -> np.ndarray:
    """The IMU's local +Z axis, expressed in its reference frame.

    Uses the driver's fused orientation quaternion if provided (per
    sensor_msgs/Imu convention, signaled by orientation_covariance[0] !=
    -1); otherwise falls back to the raw accelerometer reading, which only
    approximates "up" while the IMU is roughly static (linear_acceleration
    dominated by gravity). Either way this only recovers *tilt* (deviation
    from vertical) -- yaw is never observable from this alone.
    """

    if imu_msg.orientation_covariance[0] != -1.0:
        rot = Rotation.from_quat([
            imu_msg.orientation.x, imu_msg.orientation.y,
            imu_msg.orientation.z, imu_msg.orientation.w,
        ])
        return rot.apply([0.0, 0.0, 1.0])

    accel = np.array([
        imu_msg.linear_acceleration.x,
        imu_msg.linear_acceleration.y,
        imu_msg.linear_acceleration.z,
    ])
    norm = np.linalg.norm(accel)

    if norm < 1e-6:
        return np.array([0.0, 0.0, 1.0])

    return accel / norm


def _leveling_rotation(up_axis: np.ndarray) -> Rotation:
    """Minimal rotation mapping world +Z onto `up_axis` -- i.e. how far and
    which way something is tilted from upright, with yaw left unconstrained
    (not observable, see _imu_up_axis)."""

    rot, _ = Rotation.align_vectors([up_axis], [[0.0, 0.0, 1.0]])
    return rot


class MastPoseNode(Node):

    def __init__(self):
        super().__init__("mast_pose_node")

        self._declare_parameters()
        self._load_parameters()

        self._latest_hardware_box_imu = None
        self._latest_stereo_imu = None
        self._latest_lidar_imu = None
        self._latest_joint_state = None

        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

        self.hardware_box_imu_sub = self.create_subscription(
            Imu, self.hardware_box_imu_topic,
            self._hardware_box_imu_callback, qos_profile_sensor_data,
        )
        self.stereo_imu_sub = self.create_subscription(
            Imu, self.stereo_imu_topic,
            self._stereo_imu_callback, qos_profile_sensor_data,
        )
        self.lidar_imu_sub = self.create_subscription(
            Imu, self.lidar_imu_topic,
            self._lidar_imu_callback, qos_profile_sensor_data,
        )
        self.joint_state_sub = self.create_subscription(
            JointState, self.joint_state_topic,
            self._joint_state_callback, 10,
        )

        self.timer = self.create_timer(
            1.0 / self.publish_rate_hz, self._publish_transforms
        )

        self.get_logger().info(
            f"mast_pose_node: {self.hardware_box_imu_topic} -> "
            f"{self.world_frame}->{self.mast_base_frame}; "
            f"{self.joint_state_topic} (+ {self.stereo_imu_topic}/"
            f"{self.lidar_imu_topic} cross-check) -> "
            f"{self.mast_base_frame}->{self.mast_platform_frame}"
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def _hardware_box_imu_callback(self, msg: Imu):
        self._latest_hardware_box_imu = msg

    def _stereo_imu_callback(self, msg: Imu):
        self._latest_stereo_imu = msg

    def _lidar_imu_callback(self, msg: Imu):
        self._latest_lidar_imu = msg

    def _joint_state_callback(self, msg: JointState):
        self._latest_joint_state = msg

    def _publish_transforms(self):
        try:
            stamp = self.get_clock().now().to_msg()
            self._publish_base_transform(stamp)
            self._publish_platform_transform(stamp)
        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"_publish_transforms failed: {exc}")

    def _publish_base_transform(self, stamp):
        """world -> mast_base_link: orientation (lean) only, from the
        hardware-box IMU. Position is a deliberate placeholder -- see
        module docstring."""

        if self._latest_hardware_box_imu is None:
            self.get_logger().warn(
                "No hardware-box IMU data yet -- publishing "
                f"{self.world_frame}->{self.mast_base_frame} as level "
                "(identity rotation).",
                throttle_duration_sec=5.0,
            )
            rot = Rotation.identity()
        else:
            rot = _leveling_rotation(_imu_up_axis(self._latest_hardware_box_imu))

        self._broadcast(stamp, self.world_frame, self.mast_base_frame, (0.0, 0.0, 0.0), rot)

    def _publish_platform_transform(self, stamp):
        """mast_base_link -> mast_platform_link: pan + tilt from JointState
        (authoritative). Platform IMUs are only cross-checked against each
        other for a rigidity/fault warning, not fused into this transform."""

        if self._latest_joint_state is None:
            self.get_logger().warn(
                f"No {self.joint_state_topic} data yet -- not publishing "
                f"{self.mast_base_frame}->{self.mast_platform_frame}.",
                throttle_duration_sec=5.0,
            )
            return

        pan_angle = self._joint_position(self._latest_joint_state, self.pan_joint_name)
        tilt_angle = self._joint_position(self._latest_joint_state, self.tilt_joint_name)

        if pan_angle is None or tilt_angle is None:
            self.get_logger().warn(
                f"{self.joint_state_topic} is missing '{self.pan_joint_name}' "
                f"or '{self.tilt_joint_name}' -- not publishing "
                f"{self.mast_base_frame}->{self.mast_platform_frame}.",
                throttle_duration_sec=5.0,
            )
            return

        self._check_platform_imu_agreement()

        # Pan about the (parent) vertical axis, then tilt about the
        # already-panned platform's own axis -- standard intrinsic rotation
        # composition.
        rot = Rotation.from_euler("z", pan_angle) * Rotation.from_euler("y", tilt_angle)

        self._broadcast(
            stamp, self.mast_base_frame, self.mast_platform_frame,
            (0.0, 0.0, self.mast_height_m), rot,
        )

    def _check_platform_imu_agreement(self):
        if self._latest_stereo_imu is None or self._latest_lidar_imu is None:
            return

        up_stereo = _imu_up_axis(self._latest_stereo_imu)
        up_lidar = _imu_up_axis(self._latest_lidar_imu)

        cos_angle = float(np.clip(np.dot(up_stereo, up_lidar), -1.0, 1.0))
        disagreement_deg = math.degrees(math.acos(cos_angle))

        if disagreement_deg > self.imu_disagreement_warn_deg:
            self.get_logger().warn(
                f"Stereo- und Lidar-IMU auf der Plattform weichen um "
                f"{disagreement_deg:.1f} deg voneinander ab (Schwelle "
                f"{self.imu_disagreement_warn_deg} deg) -- Plattform nicht "
                "mehr starr, oder eine IMU liefert fehlerhafte Werte?",
                throttle_duration_sec=10.0,
            )

    def _broadcast(self, stamp, parent_frame, child_frame, translation, rotation: Rotation):
        t = TransformStamped()
        t.header.stamp = stamp
        t.header.frame_id = parent_frame
        t.child_frame_id = child_frame

        t.transform.translation.x = float(translation[0])
        t.transform.translation.y = float(translation[1])
        t.transform.translation.z = float(translation[2])

        qx, qy, qz, qw = rotation.as_quat()
        t.transform.rotation.x = float(qx)
        t.transform.rotation.y = float(qy)
        t.transform.rotation.z = float(qz)
        t.transform.rotation.w = float(qw)

        self.tf_broadcaster.sendTransform(t)

    @staticmethod
    def _joint_position(joint_state_msg: JointState, name: str):
        try:
            idx = joint_state_msg.name.index(name)
        except ValueError:
            return None

        if idx >= len(joint_state_msg.position):
            return None

        return joint_state_msg.position[idx]


def main(args=None):
    rclpy.init(args=args)

    node = MastPoseNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
