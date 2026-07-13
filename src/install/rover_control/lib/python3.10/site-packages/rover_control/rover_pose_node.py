import rclpy
from rclpy.node import Node
from std_msgs.msg import String

class RoverPoseNode(Node):

    def __init__(self):
        super().__init__("rover_pose_node")

        self.pose_publisher = self.create_publisher(
            String,
            "/rover/pose",
            10
        )

        self.get_logger().info("Rover pose node started and publishing to /rover/pose")
        
        self.timer = self.create_timer(
            5,
            self.timer_callback
        )

    def timer_callback(self):
        pose_msg = String()
        pose_msg.data = "Rover is at (x=1.0, y=2.0, theta=0.5)"
        self.pose_publisher.publish(pose_msg)

        self.get_logger().info(
            f"Published rover pose: {pose_msg.data}"
        )

def main(args=None):
    rclpy.init(args=args)

    node = RoverPoseNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":
    main()