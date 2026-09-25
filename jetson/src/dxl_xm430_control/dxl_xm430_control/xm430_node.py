#!/usr/bin/env python3
"""
ROS 2 Humble Node fuer einen Dynamixel XM430-W350-R an einem U2D2 (RS-485).

Topics (relativ zum Node-Namespace):
  Sub  ~/goal_position   std_msgs/Float64   Zielposition in rad (0 rad = Mittelstellung, Tick 2048)
  Sub  ~/goal_velocity   std_msgs/Float64   Zielgeschwindigkeit in rad/s (nur im Modus 'velocity')
  Sub  ~/torque_enable   std_msgs/Bool      Drehmoment ein/aus
  Pub  joint_states      sensor_msgs/JointState  Position [rad], Geschwindigkeit [rad/s], effort = Strom [A]
"""
import math
import threading

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64, Bool
from sensor_msgs.msg import JointState
from rover_control_msgs.msg import Housekeeping, LogMessage
from dynamixel_sdk import PortHandler, PacketHandler, COMM_SUCCESS

# --- XM430-W350 Control Table (Protokoll 2.0) ---------------------------------
ADDR_OPERATING_MODE = 11        # 1 Byte
ADDR_VELOCITY_LIMIT = 44        # 4 Byte
ADDR_TORQUE_ENABLE = 64         # 1 Byte
ADDR_HARDWARE_ERROR = 70        # 1 Byte
ADDR_GOAL_VELOCITY = 104        # 4 Byte
ADDR_PROFILE_ACCELERATION = 108 # 4 Byte
ADDR_PROFILE_VELOCITY = 112     # 4 Byte
ADDR_GOAL_POSITION = 116        # 4 Byte
ADDR_PRESENT_CURRENT = 126      # 2 Byte, direkt gefolgt von
ADDR_PRESENT_VELOCITY = 128     # 4 Byte, und
ADDR_PRESENT_POSITION = 132     # 4 Byte  -> 10 Byte am Stueck lesbar

MODES = {'velocity': 1, 'position': 3, 'extended_position': 4}
MODEL_XM430_W350 = 1020

POS_CENTER = 2048
RAD_PER_TICK = 2.0 * math.pi / 4096.0
RADS_PER_VEL_UNIT = 0.229 * 2.0 * math.pi / 60.0   # 0.229 rpm pro Einheit
AMP_PER_CUR_UNIT = 0.00269                          # 2.69 mA pro Einheit


def to_signed(value, bits):
    if value & (1 << (bits - 1)):
        value -= 1 << bits
    return value


class XM430Node(Node):

    def __init__(self):
        super().__init__('xm430_node')
        self.port = None

        # --- Parameter -------------------------------------------------------
        self.declare_parameter('port', '/dev/ttyUSB0')
        self.declare_parameter('baudrate', 57600)
        self.declare_parameter('dxl_id', 6)
        self.declare_parameter('joint_name', 'xm430_joint')
        self.declare_parameter('operating_mode', 'position')
        self.declare_parameter('profile_velocity', 50)
        self.declare_parameter('profile_acceleration', 20)
        self.declare_parameter('publish_rate', 50.0)
        self.declare_parameter('torque_off_on_shutdown', True)

        port_name = self.get_parameter('port').value
        baudrate = self.get_parameter('baudrate').value
        self.dxl_id = self.get_parameter('dxl_id').value
        self.joint_name = self.get_parameter('joint_name').value
        self.mode_name = self.get_parameter('operating_mode').value
        if self.mode_name not in MODES:
            raise ValueError(f"operating_mode muss eines von {list(MODES)} sein")

        self.lock = threading.Lock()

        # --- Verbindung aufbauen ---------------------------------------------
        self.port = PortHandler(port_name)
        self.packet = PacketHandler(2.0)

        if not self.port.openPort():
            raise RuntimeError(f'Port {port_name} konnte nicht geoeffnet werden')
        if not self.port.setBaudRate(baudrate):
            raise RuntimeError(f'Baudrate {baudrate} konnte nicht gesetzt werden')

        model, res, err = self.packet.ping(self.port, self.dxl_id)
        if res != COMM_SUCCESS:
            raise RuntimeError(
                f'Kein Dynamixel mit ID {self.dxl_id} @ {baudrate} Baud: '
                f'{self.packet.getTxRxResult(res)}')
        self.get_logger().info(f'Dynamixel ID {self.dxl_id} gefunden, Modell {model}')
        if model != MODEL_XM430_W350:
            self.get_logger().warn(f'Erwartet Modell {MODEL_XM430_W350} (XM430-W350), gefunden {model}')

        self._check_hardware_error()
        self._configure()

        # --- ROS-Schnittstellen ----------------------------------------------
        self.js_pub = self.create_publisher(Float64, '/xm430_node/new_position', 10)
        self.publish_hkd = self.create_publisher(Housekeeping, '/log/housekeeping', 10)
        self.publish_operation_log = self.create_publisher(LogMessage, '/log/operation', 10)
        self.create_subscription(Float64, '~/goal_position', self._on_goal_position, 10)
        self.create_subscription(Float64, '~/goal_velocity', self._on_goal_velocity, 10)
        self.create_subscription(Bool, '~/torque_enable', self._on_torque_enable, 10)

        rate = float(self.get_parameter('publish_rate').value)
        self.create_timer(1.0 / rate, self._publish_state)
        self.get_logger().info(f'XM430 bereit (Modus: {self.mode_name})')

    # --- Low-Level-Helfer ----------------------------------------------------
    def _write(self, size, addr, value):
        fn = {1: self.packet.write1ByteTxRx,
              2: self.packet.write2ByteTxRx,
              4: self.packet.write4ByteTxRx}[size]
        value &= (1 << (8 * size)) - 1   # negative Werte als Zweierkomplement senden
        with self.lock:
            res, err = fn(self.port, self.dxl_id, addr, value)
        if res != COMM_SUCCESS:
            self.get_logger().error(f'Schreiben Adr. {addr}: {self.packet.getTxRxResult(res)}')
            return False
        if err != 0:
            self.get_logger().error(f'Servo-Fehler Adr. {addr}: {self.packet.getRxPacketError(err)}')
            return False
        return True

    def _read(self, size, addr):
        fn = {1: self.packet.read1ByteTxRx,
              2: self.packet.read2ByteTxRx,
              4: self.packet.read4ByteTxRx}[size]
        with self.lock:
            value, res, err = fn(self.port, self.dxl_id, addr)
        if res != COMM_SUCCESS:
            raise RuntimeError(self.packet.getTxRxResult(res))
        return value

    def _check_hardware_error(self):
        hw = self._read(1, ADDR_HARDWARE_ERROR)
        if hw:
            self.get_logger().error(
                f'Hardware-Error-Status = 0x{hw:02X} (Bit0 Spannung, Bit2 Temperatur, '
                f'Bit3 Encoder, Bit4 elektr. Schock, Bit5 Ueberlast). '
                f'Servo muss neu gestartet/versorgt werden.')

    def _configure(self):
        # Betriebsmodus darf nur bei ausgeschaltetem Drehmoment geaendert werden
        self._write(1, ADDR_TORQUE_ENABLE, 0)
        self._write(1, ADDR_OPERATING_MODE, MODES[self.mode_name])
        self._write(4, ADDR_PROFILE_ACCELERATION, self.get_parameter('profile_acceleration').value)
        self._write(4, ADDR_PROFILE_VELOCITY, self.get_parameter('profile_velocity').value)
        self.vel_limit = self._read(4, ADDR_VELOCITY_LIMIT)
        self._write(1, ADDR_TORQUE_ENABLE, 1)

    # --- Callbacks -----------------------------------------------------------
    def _on_goal_position(self, msg):
        if self.mode_name == 'velocity':
            self.get_logger().warn('goal_position ignoriert: Node laeuft im Modus velocity')
            return
        ticks = int(round(msg.data / RAD_PER_TICK)) + POS_CENTER
        if self.mode_name == 'position':
            ticks = max(0, min(4095, ticks))
        else:  # extended_position: +-256 Umdrehungen
            ticks = max(-1048575, min(1048575, ticks))
        self._write(4, ADDR_GOAL_POSITION, ticks)

    def _on_goal_velocity(self, msg):
        if self.mode_name != 'velocity':
            self.get_logger().warn('goal_velocity ignoriert: Node laeuft nicht im Modus velocity')
            return
        units = int(round(msg.data / RADS_PER_VEL_UNIT))
        units = max(-self.vel_limit, min(self.vel_limit, units))
        self._write(4, ADDR_GOAL_VELOCITY, units)

    def _on_torque_enable(self, msg):
        if self._write(1, ADDR_TORQUE_ENABLE, 1 if msg.data else 0):
            self.get_logger().info(f'Drehmoment {"ein" if msg.data else "aus"}')

    def _publish_state(self):
        with self.lock:
            data, res, err = self.packet.readTxRx(
                self.port, self.dxl_id, ADDR_PRESENT_CURRENT, 10)
        if res != COMM_SUCCESS:
            self.get_logger().warn(f'Lesen fehlgeschlagen: {self.packet.getTxRxResult(res)}',
                                   throttle_duration_sec=2.0)
            return
        if err & 0x80:
            self.get_logger().error('Hardware-Fehler am Servo gemeldet!', throttle_duration_sec=2.0)

        raw = bytes(data)
        current = int.from_bytes(raw[0:2], 'little', signed=True)
        velocity = int.from_bytes(raw[2:6], 'little', signed=True)
        position = int.from_bytes(raw[6:10], 'little', signed=True)

        js = JointState()
        js.header.stamp = self.get_clock().now().to_msg()
        js.name = [self.joint_name]
        js.position = [(position - POS_CENTER) * RAD_PER_TICK]
        js.velocity = [velocity * RADS_PER_VEL_UNIT]
        js.effort = [current * AMP_PER_CUR_UNIT]   # Strom in A (kein Drehmoment!)
        msg_pos = Float64()
        msg_pos.data = float(js.position[0])
        msg_hkd = Housekeeping()
        msg_log = LogMessage()
        msg_hkd.source = "JETSON"
        msg_hkd.component = "MOTOR 5"
        msg_hkd.type = "POSITION"
        msg_hkd.vlaue = f"{msg_pos.data}"
        msg_log.source = "MOTOR 5"
        msg_log.event = "INFO"
        msg_log.message =f"Set Motor to new position: {msg_pos.data}"
        self.js_pub.publish(msg_pos)
        self.publish_hkd(msg_hkd)

    # --- Aufraeumen ----------------------------------------------------------
    def destroy_node(self):
        if self.port is not None and self.port.is_open:
            try:
                if self.get_parameter('torque_off_on_shutdown').value:
                    self._write(1, ADDR_TORQUE_ENABLE, 0)
            finally:
                self.port.closePort()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = None
    try:
        node = XM430Node()
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except Exception as e:  # noqa: BLE001
        rclpy.logging.get_logger('xm430_node').fatal(str(e))
    finally:
        if node is not None:
            node.destroy_node()
        rclpy.try_shutdown()


if __name__ == '__main__':
    main()
