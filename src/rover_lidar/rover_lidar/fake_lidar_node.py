import random

import rclpy

from rclpy.node import Node

from sensor_msgs.msg import PointCloud2
from sensor_msgs.msg import PointField
from sensor_msgs.msg import Imu

from std_msgs.msg import Header

import sensor_msgs_py.point_cloud2 as pc2


# Fake scene: instead of 4 fixed points, publish a fresh set of random points
# every cycle, all lying exactly on one fixed plane (z = A*x + B*y + C). Since
# obstacle_grid_node now buffers points per cell across callbacks (see its
# module docstring), each new random sample adds another point to whichever
# cell it falls in -- over several seconds the buffer accumulates enough
# differently-placed points per cell to make plane fitting meaningful, and
# the published /terrain/terrain_grid_stats should show a consistent
# plane_slope_deg (matching the tilt below) with roughness ~ 0 (no noise
# added -- points are exactly on the plane), which is a good sanity check
# that build_elevation_grid's weighted plane fit is working correctly.
PLANE_A = 0.02   # slope along x, m/m
PLANE_B = -0.01  # slope along y, m/m
PLANE_C = 0.30   # height at x=0, y=0, m
PLANE_X_RANGE = (0.0, 5.0)
PLANE_Y_RANGE = (0.0, 5.0)
POINTS_PER_CLOUD = 10


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

        points = []

        for _ in range(POINTS_PER_CLOUD):
            x = random.uniform(*PLANE_X_RANGE)
            y = random.uniform(*PLANE_Y_RANGE)
            z = PLANE_A * x + PLANE_B * y + PLANE_C

            points.append((x, y, z))

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
