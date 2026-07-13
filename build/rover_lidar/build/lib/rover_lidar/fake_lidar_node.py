import rclpy

from rclpy.node import Node

from sensor_msgs.msg import PointCloud2
from sensor_msgs.msg import PointField
from sensor_msgs.msg import Imu

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

        # Mid-360's built-in IMU -- matches the real livox_ros_driver2
        # topic, so mast_pose_node's platform-IMU cross-check works
        # unchanged once the real lidar is swapped in.
        self.imu_publisher = self.create_publisher(
            Imu,
            "/livox/imu",
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

        imu_msg = Imu()
        imu_msg.header.stamp = header.stamp
        imu_msg.header.frame_id = "lidar_frame"
        # Identity orientation (lidar held level) -- valid, per
        # sensor_msgs/Imu convention (orientation_covariance[0] != -1 means
        # "orientation is provided").
        imu_msg.orientation.w = 1.0
        imu_msg.orientation_covariance = [0.01, 0.0, 0.0, 0.0, 0.01, 0.0, 0.0, 0.0, 0.01]
        imu_msg.linear_acceleration.z = 9.81
        self.imu_publisher.publish(imu_msg)


def main(args=None):

    rclpy.init(args=args)

    node = FakeLidarNode()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == "__main__":
    main()
