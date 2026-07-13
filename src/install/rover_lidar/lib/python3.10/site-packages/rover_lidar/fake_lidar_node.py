import rclpy

from rclpy.node import Node

from sensor_msgs.msg import PointCloud2
from sensor_msgs.msg import PointField

from std_msgs.msg import Header

import sensor_msgs_py.point_cloud2 as pc2


class FakeLidarNode(Node):

    def __init__(self):

        super().__init__("fake_lidar_node")

        self.publisher = self.create_publisher(
            PointCloud2,
            "/livox/points",
            10
        )

        self.timer = self.create_timer(
            1.0,
            self.publish_fake_cloud
        )

        self.get_logger().info(
            "Fake LiDAR Node started"
        )

    def publish_fake_cloud(self):

        points = [

            (1.0, 0.0, 0.0),
            (1.0, 1.0, 0.0),
            (2.0, 1.0, 0.5),
            (3.0, 2.0, 1.0),

        ]

        header = Header()

        header.stamp = self.get_clock().now().to_msg()

        header.frame_id = "lidar_frame"

        cloud = pc2.create_cloud_xyz32(
            header,
            points
        )

        self.publisher.publish(cloud)

        self.get_logger().info(
            f"Published PointCloud with {len(points)} points"
        )


def main(args=None):

    rclpy.init(args=args)

    node = FakeLidarNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()