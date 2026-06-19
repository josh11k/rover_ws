import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class WifiNode(Node):

    def __init__(self):
        super().__init__("wifi_node")

        self.status_sub = self.create_subscription(
            String,
            "/commander/status",
            self.status_callback,
            10
        )

        self.get_logger().info("WiFi node started and listening to /commander/status")

    def status_callback(self, msg: String):
        self.get_logger().info(
            f"WiFi would send commander status: {msg.data}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = WifiNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()