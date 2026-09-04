import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String


class FakeUsbInterface:
    def __init__(self, port_name: str):
        self.port_name = port_name
        self.last_written_message = None

    def write(self, data: bytes):
        self.last_written_message = data.decode().strip()
        print(f"[FAKE USB WRITE to {self.port_name}] {self.last_written_message}")

    def readline(self) -> bytes:
        return b"STATUS;OK;fake_usb_active\n"

    @property
    def in_waiting(self) -> int:
        return 1


class FakeSTM32BridgeNode(Node):
    def __init__(self):
        super().__init__("fake_stm32_bridge_node")

        self.declare_parameter("port", "FAKE_USB_PORT")
        self.port = self.get_parameter("port").value

        self.usb = FakeUsbInterface(self.port)

        self.cmd_sub = self.create_subscription(
            Twist,
            "/cmd_vel",
            self.cmd_vel_callback,
            10
        )

        self.status_pub = self.create_publisher(
            String,
            "/stm32/status",
            10
        )

        self.read_timer = self.create_timer(
            7,
            self.read_from_fake_usb
        )

        self.get_logger().info(
            f"Fake STM32 Bridge started on port: {self.port}"
        )

        self.commander_status_sub = self.create_subscription(
            String,
            "/commander/status",
            self.commander_status_callback,
            10
        )

    def cmd_vel_callback(self, msg: Twist):
        usb_message = (
            f"CMD_VEL;{msg.linear.x:.2f};{msg.angular.z:.2f}\n"
        )

        self.usb.write(usb_message.encode())

    def commander_status_callback(self, msg: String):
        usb_message = f"COMMANDER_STATUS;{msg.data}\n"
        self.usb.write(usb_message.encode())

    def read_from_fake_usb(self):
        if self.usb.in_waiting > 0:
            line = self.usb.readline().decode().strip()

            status_msg = String()
            status_msg.data = line

            self.status_pub.publish(status_msg)

            self.get_logger().info(
                f"Published /stm32/status: {line}"
            )


def main(args=None):
    rclpy.init(args=args)

    node = FakeSTM32BridgeNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()