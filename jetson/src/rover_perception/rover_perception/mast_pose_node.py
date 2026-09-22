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
    mast_base_link --[pan+tilt, from MotorPosition]--> mast_platform_link

Output is a normal dynamic TF broadcast (tf2_ros.TransformBroadcaster), not
a custom "pose" message -- frame_transform_node (and anything else using
tf2's lookup_transform) already consumes whatever is in the TF tree, static
or dynamic, without needing to know this node exists.

Design decisions (see chat history for the reasoning):

- Yaw (pan) is not observable from accelerometer/gyroscope alone (gravity
  doesn't change under pure rotation about the vertical axis) -- so pan
  comes from the motor's reported position only, never "corrected" by an
  IMU here.
- Tilt (mast lean, platform tilt) IS observable via the gravity vector, but
  the motor encoder is treated as the primary/authoritative source for the
  actually-published transform. The two platform IMUs (stereo + lidar) are
  used purely as a mutual plausibility check -- since they're bolted to the
  same rigid platform, they should report the same orientation; if they
  disagree beyond imu_disagreement_warn_deg, that's logged as a
  fault/rigidity warning, not silently averaged into the transform.
- world -> mast_base_link's *position* is deliberately left at (0, 0, 0):
  determining the electronics box's actual position is explicitly a later
  task. Only its orientation (lean) is computed here.
- If an IMU's driver already provides a fused orientation quaternion, this
  node uses it directly instead of deriving one from raw accelerometer data
  (per sensor_msgs/Imu convention: orientation_covariance[0] == -1 means
  "orientation not provided", any other value means it's valid).

Pan/tilt source: MotorPosition (added 2026-09)
-----------------------------------------------------------------------------
Pan and tilt now come from stm_bridge_node's /motor_position/current
(rover_control_msgs/msg/MotorPosition, fields motor1..motor5 -- raw Dynamixel-
style servo positions, one field per physical motor on the rover, not all of
which are the mast). Per the servo datasheet: motor1 = mast tilt, motor5 =
mast pan. Raw range is 0..1023, center (i.e. 0 deg) at 512, resolution
motor_raw_to_deg (default 0.325) deg/unit -- see motor_raw_center /
motor_raw_to_deg parameters below if your hardware differs.

Graceful degradation, both dynamic transforms
-----------------------------------------------------------------------------
Neither half of the TF chain ever goes missing just because its input
hasn't arrived yet -- both _publish_base_transform() and
_publish_platform_transform() always publish *something* every tick, so
mast_platform_link (and therefore every sensor statically mounted on it)
never loses its place in the TF tree:

- world -> mast_base_link: falls back to a level (identity rotation)
  transform if no hardware-box IMU data has arrived -- see
  imu_icm20649_node.py, which has no fake fallback of its own; if it's not
  plugged in, this is simply what "no lean data" degrades to.
- mast_base_link -> mast_platform_link: falls back to pan=0, tilt=0 (mast
  upright, stationary) if no MotorPosition message has arrived yet on
  motor_position_topic -- e.g. stm_bridge_node isn't connected to the STM32
  yet. Until that source is wired up and publishing, this placeholder keeps
  the platform TF sane (upright, unmoving) rather than omitting it --
  omitting it would otherwise leave every sensor mounted on
  mast_platform_link with no TF at all, breaking frame_transform_node's
  lookups outright instead of just being "obviously not the real
  orientation".

Placeholder topics (rename via parameters once real drivers exist):
  /hardware_box/imu     -- real now: Adafruit ICM-20649 over I2C, see
                          imu_icm20649_node.py. No fake fallback -- if it's
                          not connected, this topic just has no data and
                          _publish_base_transform() falls back to level.
  /camera/imu            -- real realsense2_camera publishes this; fake_stereo_camera_node now fakes it too
  /livox/imu              -- real livox_ros_driver2 publishes this; fake_lidar_node now fakes it too
  /motor_position/current -- real now: stm_bridge_node reads this from the
                          STM32's housekeeping telemetry. No fake fallback
                          -- if it's not connected, _publish_platform_
                          transform() falls back to an upright/stationary
                          (pan=0, tilt=0) placeholder.
"""

import math

import numpy as np
from scipy.spatial.transform import Rotation

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Imu
from geometry_msgs.msg import TransformStamped
from rover_control_msgs.msg import MotorPosition

import tf2_ros


DEFAULTS = {
    "hardware_box_imu_topic": "/hardware_box/imu",
    "stereo_imu_topic": "/camera/imu",
    "lidar_imu_topic": "/livox/imu",
    "motor_position_topic": "/motor_position/current",

    "world_frame": "world",
    "mast_base_frame": "mast_base_link",
    "mast_platform_frame": "mast_platform_link",

    # Which MotorPosition field is which mast axis -- per the servo
    # datasheet: motor1 = tilt, motor5 = pan. The other three fields belong
    # to other motors on the rover (drive, etc.), not the mast.
    "pan_motor_field": "motor5",
    "tilt_motor_field": "motor1",

    # Pan-Motor: Dynamixel AX-12A (siehe Datenblatt) -- 0..1023 -> 0..300 deg,
    # Mitte (geradeaus) bei raw=512=150 deg absolut, hier relativ zur Mitte
    # gerechnet: grad = (raw - center) * deg_per_unit.
    "pan_motor_raw_center": 512,
    "pan_motor_raw_to_deg": 0.29,

    # Tilt-Motor: anderes Modell als der Pan-Motor (siehe Chat) -- eigene
    # Kalibrierung, ebenfalls relativ zur Mitte.
    "tilt_motor_raw_center": 512,
    "tilt_motor_raw_to_deg": 0.325,

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
        self._latest_motor_position = None

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
        self.motor_position_sub = self.create_subscription(
            MotorPosition, self.motor_position_topic,
            self._motor_position_callback, 10,
        )

        self.timer = self.create_timer(
            1.0 / self.publish_rate_hz, self._publish_transforms
        )

        self.get_logger().info(
            f"mast_pose_node: {self.hardware_box_imu_topic} -> "
            f"{self.world_frame}->{self.mast_base_frame}; "
            f"{self.motor_position_topic} ({self.pan_motor_field}=pan, "
            f"{self.tilt_motor_field}=tilt, + {self.stereo_imu_topic}/"
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

    def _motor_position_callback(self, msg: MotorPosition):
        self._latest_motor_position = msg

    def _raw_to_radians(self, raw: int) -> float:
        """Dynamixel-style raw position (0..1023, center 512) -> radians.

        degree = (raw - motor_raw_center) * motor_raw_to_deg. Note: the
        servo datasheet's caption literally says "Degree = Position Raw
        Data x 0.325" without an offset, but the accompanying diagram only
        makes sense with the center offset (raw=512 sits at the middle of
        the dial, i.e. 0 deg; raw=0/1023 sit at roughly +-166.7 deg, which
        only matches (raw-512)*0.325, not raw*0.325 alone). Flag if your
        servo actually wants the literal no-offset formula instead.
        """
        degrees = (raw - self.motor_raw_center) * self.motor_raw_to_deg
        return math.radians(degrees)

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
        """mast_base_link -> mast_platform_link: pan + tilt from the
        STM32's MotorPosition feedback (authoritative). Platform IMUs are
        only cross-checked against each other for a rigidity/fault
        warning, not fused into this transform.

        Falls back to pan=0, tilt=0 (mast upright, stationary) if no
        MotorPosition message has arrived yet -- e.g. stm_bridge_node
        isn't connected to the STM32 yet. See module docstring "Graceful
        degradation" section.
        """

        if self._latest_motor_position is None:
            self.get_logger().warn(
                f"No {self.motor_position_topic} data yet -- publishing "
                f"{self.mast_base_frame}->{self.mast_platform_frame} as "
                "an upright/stationary placeholder (pan=0, tilt=0).",
                throttle_duration_sec=5.0,
            )
            pan_angle = 0.0
            tilt_angle = 0.0
        else:
            pan_raw = getattr(self._latest_motor_position, self.pan_motor_field)
            tilt_raw = getattr(self._latest_motor_position, self.tilt_motor_field)

            pan_angle = self._raw_to_radians(pan_raw)
            tilt_angle = self._raw_to_radians(tilt_raw)

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