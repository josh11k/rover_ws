import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class FakeSTM32BridgeNode(Node):

    def __init__(self):
        super().__init__("fake_stm32_bridge_node")

        self.subscription = self.create_subscription(
            Twist,
            "/cmd_vel",
            self.cmd_vel_callback,
            10
        )

    def cmd_vel_callback(self, msg):
        self.get_logger().info(
            f"Received cmd_vel: linear={msg.linear.x}, angular={msg.angular.z}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = FakeSTM32BridgeNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()