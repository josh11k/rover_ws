"""Compute the mast's dynamic TF chain from motor positions + IMUs.

This is the "Int_pose_node" concept from the original diagram, properly
scoped: the perception module sits on a ~1.2m mast that can pan (rotate at
the base) and carries a tiltable platform (lidar/stereo/mono cam mounted
rigidly on it) at its tip. Pan/tilt angle come from motor feedback; a third
IMU sits in the electronics box further down the mast to catch mast lean.

This node owns exactly the two frames that are genuinely dynamic:

    world --[orientation only, from hardware-box IMU]--> mast_base_link
    mast_base_link --[pan + tilt, from motor feedback]--> mast_platform_link

Pan / tilt sources
-----------------------------------------------------------------------------
- PAN  = XM430 (Motor 5) via xm430_node: /xm430_node/current_position,
         std_msgs/Float64 in RADIANS (0 rad = tick 2048).
- TILT = HerkuleX Motor 1 via STM32 housekeeping -> stm_bridge_node ->
         /motor_position/current_position (MotorPosition.motor1, raw 0..1023).

Hardware-box IMU -> world frame (NEU 2026-10)
-----------------------------------------------------------------------------
world -> mast_base_link is the mast LEAN only (roll/pitch from gravity; yaw is
not observable without a magnetometer and stays 0; position stays 0,0,0).
Processing per IMU message:
  1. Plausibility: samples whose |accel| is far from 1 g (imu_accel_tolerance)
     are dropped -- they contain motion/vibration, not just gravity.
  2. Mounting: the measured 'up' vector is rotated from the IMU's own frame
     into mast_base_link via imu_mount_roll/pitch/yaw (same convention as a
     static_transform_publisher: orientation of the IMU frame expressed in
     mast_base_link). All 0 = IMU axes exactly X forward / Y left / Z up.
  3. Low-pass: exponential moving average with time constant
     imu_filter_tau_sec, so vibrations / motor moves don't make the world
     frame jitter. The mast lean only changes slowly.
  4. Level offset (zero calibration): imu_level_roll_offset /
     imu_level_pitch_offset remove a constant mounting error. Set them with
         ros2 service call /calibrate_imu_level std_srvs/srv/Trigger {}
     while the mast stands on LEVEL ground -- the node measures the current
     lean, stores it as "level" (active immediately) and logs the two values
     so you can put them into the launch file permanently.
If no IMU data has ever arrived, world == mast_base_link (identity). If data
stops arriving, the last filtered lean is held (with a warning).

Graceful degradation (platform)
-----------------------------------------------------------------------------
no pan feedback -> pan = 0, no tilt feedback -> tilt = 0. Both transforms are
published every tick, never omitted.
"""

import math

import numpy as np
from scipy.spatial.transform import Rotation

import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Imu
from std_msgs.msg import Float64
from std_srvs.srv import Trigger
from geometry_msgs.msg import TransformStamped
from rover_control_msgs.msg import MotorPosition

import tf2_ros


GRAVITY = 9.80665
EZ = np.array([0.0, 0.0, 1.0])

DEFAULTS = {
    "hardware_box_imu_topic": "/hardware_box/imu",
    "stereo_imu_topic": "/camera/imu",
    "lidar_imu_topic": "/livox/imu",

    # TILT: HerkuleX Motor 1 aus dem STM-Housekeeping (MotorPosition.motor1)
    "motor_position_topic": "/motor_position/current_position",
    "tilt_motor_field": "motor1",
    "tilt_motor_raw_center": 265,     # raw-Wert, bei dem die Plattform waagrecht ist -- KALIBRIEREN
    "tilt_motor_raw_to_deg": 0.325,   # HerkuleX DRS-0101: 0.325 deg/raw
    "tilt_sign": -1.0,                # -1.0, falls die Plattform in RViz falsch herum kippt

    # PAN: XM430 (Motor 5) aus dem xm430_node, bereits in Radiant
    "pan_topic": "/xm430_node/current_position",
    "pan_offset_rad": 0.0,            # Winkel, bei dem Plattform-X = Mastbasis-X -- KALIBRIEREN
    "pan_sign": 1.0,                  # -1.0, falls die Wolke beim Drehen gegenlaeufig rotiert

    "world_frame": "world",
    "mast_base_frame": "mast_base_link",
    "mast_platform_frame": "mast_platform_link",

    # Fixed height of the platform's tilt-joint pivot above mast_base_link.
    "mast_height_m": 1.20,

    # --- NEU: Box-IMU -> world -------------------------------------------
    # Einbaulage der IMU in mast_base_link (rad), Konvention wie
    # static_transform_publisher. Alle 0 = IMU-Achsen x vorne/y links/z oben.
    "imu_mount_roll": 0.0,
    "imu_mount_pitch": 0.0,
    "imu_mount_yaw": 0.0,
    # Tiefpass-Zeitkonstante (s). Groesser = ruhiger, aber traeger.
    "imu_filter_tau_sec": 1.0,
    # Messwerte verwerfen, deren Betrag mehr als so viel (m/s^2) von 1 g
    # abweicht (Bewegung/Stoss statt nur Schwerkraft).
    "imu_accel_tolerance": 1.5,
    # Nach so vielen Sekunden ohne IMU-Daten wird gewarnt (letzter Wert bleibt).
    "imu_timeout_sec": 2.0,
    # Nullabgleich (rad) -- per Service calibrate_imu_level ermitteln und
    # dann fest in die Launch-Datei eintragen.
    "imu_level_roll_offset": 0.0,
    "imu_level_pitch_offset": 0.0,
    # Aktuelle Mastneigung alle N Sekunden ins Log schreiben (0 = aus).
    "imu_log_period_sec": 10.0,

    "imu_disagreement_warn_deg": 5.0,

    "publish_rate_hz": 20.0,
}


def _imu_up_axis(imu_msg: Imu) -> np.ndarray:
    """Unit 'up' direction from one IMU message -- used ONLY for the
    platform-IMU cross-check (comparing two IMUs of the same kind)."""

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


class MastPoseNode(Node):

    def __init__(self):
        super().__init__("mast_pose_node")

        self._declare_parameters()
        self._load_parameters()

        self._latest_stereo_imu = None
        self._latest_lidar_imu = None
        self._latest_motor_position = None
        self._latest_pan_rad = None

        # NEU: gefilterte 'oben'-Richtung in mast_base_link-Koordinaten
        self._filtered_up = None
        self._last_imu_stamp_s = None   # fuer die Filter-Zeitschritte
        self._last_imu_rx_s = None      # fuer den Timeout
        self._last_lean_log_s = 0.0
        self._update_imu_rotations()

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
        self.pan_sub = self.create_subscription(
            Float64, self.pan_topic,
            self._pan_callback, 10,
        )

        # NEU: Nullabgleich der Box-IMU
        self.calibrate_srv = self.create_service(
            Trigger, "calibrate_imu_level", self._calibrate_imu_level_callback,
        )

        self.timer = self.create_timer(
            1.0 / self.publish_rate_hz, self._publish_transforms
        )

        self.get_logger().info(
            f"mast_pose_node: {self.hardware_box_imu_topic} -> "
            f"{self.world_frame}->{self.mast_base_frame} "
            f"(tau {self.imu_filter_tau_sec}s, mount rpy "
            f"{self.imu_mount_roll:.3f}/{self.imu_mount_pitch:.3f}/{self.imu_mount_yaw:.3f}, "
            f"level offset {self.imu_level_roll_offset:.4f}/{self.imu_level_pitch_offset:.4f}); "
            f"pan from {self.pan_topic}, tilt from "
            f"{self.motor_position_topic}.{self.tilt_motor_field} "
            f"(center {self.tilt_motor_raw_center}) -> "
            f"{self.mast_base_frame}->{self.mast_platform_frame}"
        )

    # ------------------------------------------------------------------
    # Parameter
    # ------------------------------------------------------------------
    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def _update_imu_rotations(self):
        # Einbaulage: Orientierung des IMU-Frames in mast_base_link
        # (scipy 'xyz' klein = extrinsisch = Rz(yaw)*Ry(pitch)*Rx(roll),
        # identisch zur static_transform_publisher-Konvention).
        self._r_mount = Rotation.from_euler(
            "xyz", [self.imu_mount_roll, self.imu_mount_pitch, self.imu_mount_yaw]
        )
        # Nullabgleich: dreht die gemessene 'oben'-Richtung so, dass die beim
        # Kalibrieren gemessene Neigung als waagrecht gilt.
        self._r_level = Rotation.from_euler(
            "xy", [self.imu_level_roll_offset, self.imu_level_pitch_offset]
        )

    # ------------------------------------------------------------------
    # Callbacks
    # ------------------------------------------------------------------
    def _imu_up_in_base(self, msg: Imu):
        """'Oben' (Weltrichtung entgegen der Schwerkraft) in mast_base_link-
        Koordinaten, ohne Nullabgleich. None, wenn der Messwert unbrauchbar ist."""

        if msg.orientation_covariance[0] != -1.0:
            # Fusionierte Orientierung q (Sensor -> Welt): Welt-oben im Sensor = q^-1 * ez
            q = Rotation.from_quat([
                msg.orientation.x, msg.orientation.y,
                msg.orientation.z, msg.orientation.w,
            ])
            up_sensor = q.inv().apply(EZ)
        else:
            accel = np.array([
                msg.linear_acceleration.x,
                msg.linear_acceleration.y,
                msg.linear_acceleration.z,
            ])
            norm = float(np.linalg.norm(accel))
            if abs(norm - GRAVITY) > self.imu_accel_tolerance:
                return None  # Bewegung/Stoss -> nicht nur Schwerkraft
            # Ruhender Beschleunigungsmesser misst +1 g nach OBEN (Gegenkraft)
            up_sensor = accel / norm

        return self._r_mount.apply(up_sensor)

    def _hardware_box_imu_callback(self, msg: Imu):
        now_s = self.get_clock().now().nanoseconds * 1e-9
        self._last_imu_rx_s = now_s

        up = self._imu_up_in_base(msg)
        if up is None:
            return

        stamp_s = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        if stamp_s <= 0.0:
            stamp_s = now_s

        if self._filtered_up is None or self._last_imu_stamp_s is None:
            self._filtered_up = up
        else:
            dt = min(max(stamp_s - self._last_imu_stamp_s, 0.0), 1.0)
            tau = max(self.imu_filter_tau_sec, 0.0)
            alpha = 1.0 if tau == 0.0 else dt / (tau + dt)
            filtered = (1.0 - alpha) * self._filtered_up + alpha * up
            n = np.linalg.norm(filtered)
            if n > 1e-9:
                self._filtered_up = filtered / n

        self._last_imu_stamp_s = stamp_s

    def _stereo_imu_callback(self, msg: Imu):
        self._latest_stereo_imu = msg

    def _lidar_imu_callback(self, msg: Imu):
        self._latest_lidar_imu = msg

    def _motor_position_callback(self, msg: MotorPosition):
        self._latest_motor_position = msg

    def _pan_callback(self, msg: Float64):
        self._latest_pan_rad = float(msg.data)

    def _calibrate_imu_level_callback(self, request, response):
        """Aktuelle (gefilterte) Neigung als 'waagrecht' uebernehmen."""
        if self._filtered_up is None:
            response.success = False
            response.message = (
                "Keine gueltigen IMU-Daten -- Box-IMU angeschlossen und Mast in Ruhe?"
            )
            return response

        r_zero, _ = Rotation.align_vectors([EZ], [self._filtered_up])
        roll, pitch, _yaw = r_zero.as_euler("xyz")

        self.set_parameters([
            Parameter("imu_level_roll_offset", value=float(roll)),
            Parameter("imu_level_pitch_offset", value=float(pitch)),
        ])
        self.imu_level_roll_offset = float(roll)
        self.imu_level_pitch_offset = float(pitch)
        self._update_imu_rotations()

        response.success = True
        response.message = (
            f"IMU-Nullabgleich gesetzt: imu_level_roll_offset={roll:.5f}, "
            f"imu_level_pitch_offset={pitch:.5f} (rad) -- fuer dauerhaft in die "
            f"Launch-Datei (mast_pose-Block) eintragen."
        )
        self.get_logger().info(response.message)
        return response

    # ------------------------------------------------------------------
    # TF
    # ------------------------------------------------------------------
    def _tilt_raw_to_radians(self, raw: int) -> float:
        degrees = (raw - self.tilt_motor_raw_center) * self.tilt_motor_raw_to_deg
        return self.tilt_sign * math.radians(degrees)

    def _publish_transforms(self):
        stamp = self.get_clock().now().to_msg()
        try:
            self._publish_base_transform(stamp)
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f"base transform failed: {exc}", throttle_duration_sec=5.0)
        try:
            self._publish_platform_transform(stamp)
        except Exception as exc:  # noqa: BLE001
            self.get_logger().error(f"platform transform failed: {exc}", throttle_duration_sec=5.0)

    def _publish_base_transform(self, stamp):
        """world -> mast_base_link: Mastneigung aus der gefilterten Box-IMU."""

        if self._filtered_up is None:
            self.get_logger().warn(
                "No (valid) hardware-box IMU data yet -- publishing "
                f"{self.world_frame}->{self.mast_base_frame} as level.",
                throttle_duration_sec=5.0,
            )
            rot = Rotation.identity()
        else:
            now_s = self.get_clock().now().nanoseconds * 1e-9
            if self._last_imu_rx_s is not None and now_s - self._last_imu_rx_s > self.imu_timeout_sec:
                self.get_logger().warn(
                    f"No hardware-box IMU data for {now_s - self._last_imu_rx_s:.1f}s -- "
                    "holding last mast lean.",
                    throttle_duration_sec=5.0,
                )

            up = self._r_level.apply(self._filtered_up)
            # Rotation mast_base -> world: gemessenes 'oben' auf Welt-z abbilden
            rot, _ = Rotation.align_vectors([EZ], [up])

            if self.imu_log_period_sec > 0.0 and now_s - self._last_lean_log_s >= self.imu_log_period_sec:
                self._last_lean_log_s = now_s
                roll, pitch, _ = rot.as_euler("xyz", degrees=True)
                self.get_logger().info(
                    f"Mastneigung: roll {roll:+.2f} deg, pitch {pitch:+.2f} deg"
                )

        self._broadcast(stamp, self.world_frame, self.mast_base_frame, (0.0, 0.0, 0.0), rot)

    def _publish_platform_transform(self, stamp):
        """mast_base_link -> mast_platform_link: pan (XM430) + tilt (HerkuleX
        motor 1). Missing inputs fall back to 0 independently."""

        if self._latest_pan_rad is None:
            self.get_logger().warn(
                f"No {self.pan_topic} data yet -- using pan = 0.",
                throttle_duration_sec=5.0,
            )
            pan_angle = 0.0
        else:
            pan_angle = self.pan_sign * (self._latest_pan_rad - self.pan_offset_rad)

        tilt_angle = 0.0
        if self._latest_motor_position is None:
            self.get_logger().warn(
                f"No {self.motor_position_topic} data yet -- using tilt = 0.",
                throttle_duration_sec=5.0,
            )
        else:
            tilt_raw = getattr(self._latest_motor_position, self.tilt_motor_field)
            if tilt_raw < 0:
                self.get_logger().warn(
                    f"{self.tilt_motor_field} unknown (-1) -- using tilt = 0.",
                    throttle_duration_sec=5.0,
                )
            else:
                tilt_angle = self._tilt_raw_to_radians(tilt_raw)

        self._check_platform_imu_agreement()

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
                f"{self.imu_disagreement_warn_deg} deg) -- unterschiedliche "
                "Einbaulage der IMUs, Plattform nicht starr, oder fehlerhafte Werte?",
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