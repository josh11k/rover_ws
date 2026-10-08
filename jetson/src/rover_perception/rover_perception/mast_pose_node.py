"""Compute the mast's dynamic TF chain from motor positions + IMUs.

This is the "Int_pose_node" concept from the original diagram, properly
scoped: the perception module sits on a ~1.2m mast that can pan (rotate at
the base) and carries a tiltable platform (lidar/stereo/mono cam mounted
rigidly on it) at its tip. Pan/tilt angle come from motor feedback; a third
IMU sits in the electronics box further down the mast to catch mast lean.

This node owns exactly the two frames that are genuinely dynamic, and
nothing else -- the sensor-to-platform offsets stay where they already are
(static_transform_publisher in the launch file), because they're fixed by
mechanical design, not something a motor or IMU reports:

    world --[orientation only, from hardware-box IMU]--> mast_base_link
    mast_base_link --[pan + tilt, from motor feedback]--> mast_platform_link

Output is a normal dynamic TF broadcast (tf2_ros.TransformBroadcaster) --
frame_transform_node (and anything else using tf2's lookup_transform)
consumes it without needing to know this node exists.

Design decisions:

- Yaw (pan) is not observable from accelerometer/gyroscope alone -- pan
  comes from the motor's reported position only.
- Tilt is taken from the motor encoder (authoritative). The two platform
  IMUs (stereo + lidar) are only a mutual plausibility check.
- world -> mast_base_link's *position* stays at (0, 0, 0) (later task);
  only its orientation (lean) is computed here. NOTE: the map is built in
  mast_base_link, so this lean currently does NOT affect the map -- it only
  matters for consumers working in the world frame.

Pan / tilt sources (GEÄNDERT 2026-10)
-----------------------------------------------------------------------------
- PAN  = Dynamixel XM430-W350 (Motor 5), via xm430_node:
         /xm430_node/current_position, std_msgs/Float64, RADIANS,
         0 rad = xm430_node's center (tick 2048). Real Present_Position,
         published at ~50 Hz. Calibrate with pan_offset_rad / pan_sign.
         (Vorher: motor5 aus MotorPosition -- dieses Feld existiert nicht
         mehr, MotorPosition hat nur motor1..motor4.)
- TILT = HerkuleX Motor 1 via STM32 housekeeping -> stm_bridge_node ->
         /motor_position/current_position (MotorPosition.motor1), raw
         0..1023, deg = (raw - tilt_motor_raw_center) * tilt_motor_raw_to_deg.
         Only every ~5 s (housekeeping rate); the last value is held.

Graceful degradation
-----------------------------------------------------------------------------
Both transforms are published every tick, never omitted:
- no hardware-box IMU -> world->mast_base_link level (identity)
- no pan feedback     -> pan = 0
- no tilt feedback    -> tilt = 0
so mast_platform_link (and every sensor mounted on it) always exists in TF.
"""

import math

import numpy as np
from scipy.spatial.transform import Rotation

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Imu
from std_msgs.msg import Float64
from geometry_msgs.msg import TransformStamped
from rover_control_msgs.msg import MotorPosition

import tf2_ros


DEFAULTS = {
    "hardware_box_imu_topic": "/hardware_box/imu",
    "stereo_imu_topic": "/camera/imu",
    "lidar_imu_topic": "/livox/imu",

    # TILT: HerkuleX Motor 1 aus dem STM-Housekeeping (MotorPosition.motor1)
    "motor_position_topic": "/motor_position/current_position",
    "tilt_motor_field": "motor1",
    "tilt_motor_raw_center": 512,     # raw-Wert, bei dem die Plattform waagrecht ist -- KALIBRIEREN
    "tilt_motor_raw_to_deg": 0.325,   # HerkuleX DRS-0101: 0.325 deg/raw
    "tilt_sign": 1.0,                 # -1.0, falls die Plattform in RViz falsch herum kippt

    # PAN: XM430 (Motor 5) aus dem xm430_node, bereits in Radiant
    "pan_topic": "/xm430_node/current_position",
    "pan_offset_rad": 0.0,            # Winkel, bei dem Plattform-X = Mastbasis-X -- KALIBRIEREN
    "pan_sign": 1.0,                  # -1.0, falls die Wolke beim Drehen gegenlaeufig rotiert

    "world_frame": "world",
    "mast_base_frame": "mast_base_link",
    "mast_platform_frame": "mast_platform_link",

    # Fixed height of the platform's tilt-joint pivot above mast_base_link.
    # Placeholder -- replace with the measured mast height.
    "mast_height_m": 1.20,

    "imu_disagreement_warn_deg": 5.0,

    "publish_rate_hz": 20.0,
}


def _imu_up_axis(imu_msg: Imu) -> np.ndarray:
    """Unit 'up' direction derived from one IMU message -- used ONLY for the
    platform-IMU cross-check (comparing two IMUs of the same kind), where
    the convention just has to be consistent, not absolute."""

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


def _imu_tilt_rotation(imu_msg: Imu) -> Rotation:
    """Tilt-only rotation sensor -> world (yaw left at 0, not observable).

    GEÄNDERT: the two cases need OPPOSITE handling:
    - fused orientation q (sensor -> world): the sensor's +Z expressed in
      world is q*ez; the rotation mapping ez onto that is the tilt of q.
    - raw accelerometer (static): the measured vector is WORLD-up expressed
      in SENSOR coordinates (= q^-1 * ez), so the rotation must map that
      vector onto ez -- the inverse direction. The old code treated both
      the same way, which mirrored the lean for accel-only IMUs (the
      ICM-20649 node publishes accel only, orientation_covariance[0] = -1).
    """
    ez = np.array([0.0, 0.0, 1.0])

    if imu_msg.orientation_covariance[0] != -1.0:
        q = Rotation.from_quat([
            imu_msg.orientation.x, imu_msg.orientation.y,
            imu_msg.orientation.z, imu_msg.orientation.w,
        ])
        sensor_z_in_world = q.apply(ez)
        rot, _ = Rotation.align_vectors([sensor_z_in_world], [ez])
        return rot

    accel = np.array([
        imu_msg.linear_acceleration.x,
        imu_msg.linear_acceleration.y,
        imu_msg.linear_acceleration.z,
    ])
    norm = np.linalg.norm(accel)
    if norm < 1e-6:
        return Rotation.identity()

    world_up_in_sensor = accel / norm
    rot, _ = Rotation.align_vectors([ez], [world_up_in_sensor])
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
        self._latest_pan_rad = None   # NEU: Pan direkt vom xm430_node

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
        # NEU: Pan-Feedback
        self.pan_sub = self.create_subscription(
            Float64, self.pan_topic,
            self._pan_callback, 10,
        )

        self.timer = self.create_timer(
            1.0 / self.publish_rate_hz, self._publish_transforms
        )

        self.get_logger().info(
            f"mast_pose_node: {self.hardware_box_imu_topic} -> "
            f"{self.world_frame}->{self.mast_base_frame}; "
            f"pan from {self.pan_topic} (rad, offset {self.pan_offset_rad}), "
            f"tilt from {self.motor_position_topic}.{self.tilt_motor_field} "
            f"(center {self.tilt_motor_raw_center}, {self.tilt_motor_raw_to_deg} deg/raw) -> "
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

    def _pan_callback(self, msg: Float64):
        self._latest_pan_rad = float(msg.data)

    def _tilt_raw_to_radians(self, raw: int) -> float:
        """HerkuleX raw (0..1023) -> radians, relative to the level position.

        GEÄNDERT: used self.motor_raw_center / self.motor_raw_to_deg before,
        which don't exist as parameters -> AttributeError on the first
        MotorPosition message, and the platform TF was then never published.
        """
        degrees = (raw - self.tilt_motor_raw_center) * self.tilt_motor_raw_to_deg
        return self.tilt_sign * math.radians(degrees)

    def _publish_transforms(self):
        stamp = self.get_clock().now().to_msg()
        # GEÄNDERT: getrennt abgesichert -- ein Fehler in einem Teil darf den
        # anderen Transform nicht mehr mitreissen.
        try:
            self._publish_base_transform(stamp)
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f"base transform failed: {exc}", throttle_duration_sec=5.0)
        try:
            self._publish_platform_transform(stamp)
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f"platform transform failed: {exc}", throttle_duration_sec=5.0)

    def _publish_base_transform(self, stamp):
        """world -> mast_base_link: orientation (lean) only, from the
        hardware-box IMU. Assumes the IMU axes are aligned with
        mast_base_link (X forward, Y left, Z up)."""

        if self._latest_hardware_box_imu is None:
            self.get_logger().warn(
                "No hardware-box IMU data yet -- publishing "
                f"{self.world_frame}->{self.mast_base_frame} as level "
                "(identity rotation).",
                throttle_duration_sec=5.0,
            )
            rot = Rotation.identity()
        else:
            rot = _imu_tilt_rotation(self._latest_hardware_box_imu)

        self._broadcast(stamp, self.world_frame, self.mast_base_frame, (0.0, 0.0, 0.0), rot)

    def _publish_platform_transform(self, stamp):
        """mast_base_link -> mast_platform_link: pan (XM430) + tilt (HerkuleX
        motor 1). Missing inputs fall back to 0 independently."""

        # --- Pan ---
        if self._latest_pan_rad is None:
            self.get_logger().warn(
                f"No {self.pan_topic} data yet -- using pan = 0.",
                throttle_duration_sec=5.0,
            )
            pan_angle = 0.0
        else:
            pan_angle = self.pan_sign * (self._latest_pan_rad - self.pan_offset_rad)

        # --- Tilt ---
        tilt_angle = 0.0
        if self._latest_motor_position is None:
            self.get_logger().warn(
                f"No {self.motor_position_topic} data yet -- using tilt = 0.",
                throttle_duration_sec=5.0,
            )
        else:
            tilt_raw = getattr(self._latest_motor_position, self.tilt_motor_field)
            if tilt_raw < 0:
                # stm_bridge_node setzt -1 fuer "unbekannt" -- dann waagrecht annehmen
                self.get_logger().warn(
                    f"{self.tilt_motor_field} unknown (-1) -- using tilt = 0.",
                    throttle_duration_sec=5.0,
                )
            else:
                tilt_angle = self._tilt_raw_to_radians(tilt_raw)

        self._check_platform_imu_agreement()

        # Pan about the (parent) vertical axis, then tilt about the
        # already-panned platform's own Y axis (intrinsic composition).
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
                "mehr starr, unterschiedliche Einbaulage der IMUs, oder eine "
                "IMU liefert fehlerhafte Werte?",
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