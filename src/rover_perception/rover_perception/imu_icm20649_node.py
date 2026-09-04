"""Real driver for an Adafruit ICM-20649 (6-DOF accel+gyro, no magnetometer,
no onboard sensor fusion) wired to the Jetson's 40-pin header I2C bus
(3.3V -> pin 1, SDA -> pin 3, SCL -> pin 5, GND -> pin 9).

Unlike fake_mast_hw_node's fake IMU (which fakes a fused orientation
quaternion) this chip has no fusion -- it only gives raw linear_acceleration
(m/s^2) and angular_velocity (rad/s). orientation is left at all-zero with
orientation_covariance[0] = -1, which is the sensor_msgs/Imu convention for
"this field is not populated" -- consumers (e.g. an EKF / madgwick filter)
should compute orientation themselves rather than trust a zero quaternion.

Uses Adafruit's CircuitPython driver (adafruit-circuitpython-icm20x, via
Blinka) rather than a hand-rolled register driver -- the ICM-20649's
register-bank switching is fiddly to get right by hand and Adafruit's
driver is already tested against this exact chip.

Setup (see chat for the full walkthrough):
    sudo apt install -y i2c-tools python3-smbus
    pip3 install --user adafruit-blinka adafruit-circuitpython-icm20x
    sudo i2cdetect -y -r <bus>   # find the bus number + confirm address (0x68/0x69)

Standalone sanity check before running this node:
    python3 -c "
import board, busio
from adafruit_icm20x import ICM20649
i2c = busio.I2C(board.SCL, board.SDA)
imu = ICM20649(i2c, address=0x68)
print(imu.acceleration, imu.gyro)
"

This is the ONLY hardware-box IMU source in the project now -- there is no
fake fallback (see fake_mast_hw_node.py, which used to fake this). If the
sensor isn't wired up / doesn't respond on I2C, this node stays alive and
simply never publishes; mast_pose_node already handles "no hardware-box IMU
data yet" gracefully (falls back to a level/identity mast_base transform,
see its _publish_base_transform), so the rest of the pipeline degrades
cleanly rather than crashing.

Reconnect behavior: sensor init is retried on a timer (reconnect_period_sec)
until it succeeds, so plugging the IMU in after the node has already
started still works -- you don't need to restart the launch file.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Imu

import board
import busio
from adafruit_icm20x import ICM20649


DEFAULTS = {
    "imu_topic": "/hardware_box/imu",
    "frame_id": "hardware_box_link",
    "publish_rate_hz": 50.0,

    # Adafruit ICM-20649 default I2C address is 0x68 (0x69 if the board's
    # AD0 pin is tied high instead of left floating/grounded).
    "i2c_address": 0x68,

    # How often to retry connecting to the sensor while it's absent/not
    # responding (e.g. not plugged in yet, or a loose wire).
    "reconnect_period_sec": 5.0,

    # Not measured -- placeholder diagonal covariances. Replace once you've
    # characterized the actual sensor noise (e.g. Allan variance at rest).
    "linear_acceleration_covariance_diag": 0.05,
    "angular_velocity_covariance_diag": 0.01,
}


class ImuIcm20649Node(Node):

    def __init__(self):
        super().__init__("imu_icm20649_node")

        self._declare_parameters()
        self._load_parameters()

        self.imu = None  # None until _try_connect() succeeds

        self.pub = self.create_publisher(
            Imu, self.imu_topic, qos_profile_sensor_data,
        )

        self._try_connect()

        period = 1.0 / self.publish_rate_hz
        self.timer = self.create_timer(period, self.timer_callback)
        self.reconnect_timer = self.create_timer(
            self.reconnect_period_sec, self._try_connect
        )

        self.get_logger().info(
            f"imu_icm20649_node: I2C 0x{self.i2c_address:02x} -> "
            f"{self.imu_topic} @ {self.publish_rate_hz} Hz "
            f"(frame_id={self.frame_id}, no orientation -- accel+gyro only). "
            "No fake fallback -- if the sensor isn't connected, this topic "
            "simply won't publish (see module docstring)."
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def _try_connect(self):
        """(Re)attempt to bring up the I2C sensor. Safe to call repeatedly
        -- a no-op once self.imu is already set. Never raises: on failure
        this just logs and leaves self.imu as None so timer_callback keeps
        skipping publishes until a later retry succeeds."""

        if self.imu is not None:
            return

        try:
            i2c = busio.I2C(board.SCL, board.SDA)
            self.imu = ICM20649(i2c, address=self.i2c_address)
            self.get_logger().info(
                f"imu_icm20649_node: connected to ICM-20649 at "
                f"0x{self.i2c_address:02x}"
            )
        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().warn(
                f"ICM-20649 not available on I2C (0x{self.i2c_address:02x}): "
                f"{exc}. No hardware-box IMU data until it's connected -- "
                f"retrying every {self.reconnect_period_sec}s.",
                throttle_duration_sec=self.reconnect_period_sec,
            )
            self.imu = None

    def timer_callback(self):
        if self.imu is None:
            # Not connected -- nothing to publish. _try_connect() (its own
            # timer) will pick it up once the sensor responds.
            return

        try:
            ax, ay, az = self.imu.acceleration  # m/s^2
            gx, gy, gz = self.imu.gyro          # rad/s
        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(
                f"Failed to read ICM-20649 over I2C: {exc}",
                throttle_duration_sec=5.0,
            )
            # Drop the (presumably now-stale/disconnected) handle so
            # _try_connect() re-initializes it instead of hammering a dead
            # bus with reads forever.
            self.imu = None
            return

        msg = Imu()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.frame_id

        # No orientation from this chip -- mark it explicitly unset per the
        # sensor_msgs/Imu convention (first covariance entry == -1).
        msg.orientation_covariance[0] = -1.0

        msg.linear_acceleration.x = ax
        msg.linear_acceleration.y = ay
        msg.linear_acceleration.z = az
        msg.linear_acceleration_covariance = [
            self.linear_acceleration_covariance_diag, 0.0, 0.0,
            0.0, self.linear_acceleration_covariance_diag, 0.0,
            0.0, 0.0, self.linear_acceleration_covariance_diag,
        ]

        msg.angular_velocity.x = gx
        msg.angular_velocity.y = gy
        msg.angular_velocity.z = gz
        msg.angular_velocity_covariance = [
            self.angular_velocity_covariance_diag, 0.0, 0.0,
            0.0, self.angular_velocity_covariance_diag, 0.0,
            0.0, 0.0, self.angular_velocity_covariance_diag,
        ]

        self.pub.publish(msg)


def main(args=None):
    rclpy.init(args=args)

    node = ImuIcm20649Node()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
