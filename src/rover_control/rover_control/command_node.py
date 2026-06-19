import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String


class CommandNode(Node):

    def __init__(self):
        super().__init__("command_node")

        self.publisher = self.create_publisher(
            Twist,
            "/cmd_vel",
            10
        )

        self.status_publisher = self.create_publisher(
            String,
            "/commander/status",
            10
        )

        self.timer = self.create_timer(
            5,
            self.timer_callback
        )

    def timer_callback(self):
        status_msg = String()
        msg = Twist()

        msg.linear.x = 0.2
        msg.angular.z = 0.0
        status_msg.data = "COMMANDER_ACTIVE"

        self.status_publisher.publish(status_msg)
        self.publisher.publish(msg)

        self.get_logger().info(
            f"Published /cmd_vel: linear.x={msg.linear.x}, angular.z={msg.angular.z}"
        )


def main(args=None):
    rclpy.init(args=args)

    node = CommandNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()