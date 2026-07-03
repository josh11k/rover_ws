"""Generic PointCloud2 frame-transform node.

Replaces the hand-drawn diagram's separate "turn_pointcloud_node" (lidar
branch) and the pose-transform step on the stereo branch with a single
reusable node type. Instead of manually wiring a "pose" topic from an
Int_pose_node into every consumer, this node looks up the sensor -> target
frame transform via the standard ROS2 tf2 tree (static extrinsics published
by a static_transform_publisher, dynamic transforms published once the
IMU-fusion / localization pipeline exists) and republishes the cloud already
expressed in the target frame.

Run one instance per sensor via launch args, e.g.:

    frame_transform_node --ros-args \
        -p input_topic:=/livox/points \
        -p output_topic:=/lidar/points_mast_base_link \
        -p target_frame:=mast_base_link

The node degrades gracefully (skips the frame, logs a throttled warning) if
no transform is available yet, e.g. because the extrinsic calibration has
not been published, rather than crashing the pipeline.
"""

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import PointCloud2

import tf2_ros
from tf2_sensor_msgs.tf2_sensor_msgs import do_transform_cloud


DEFAULTS = {
    "input_topic": "/livox/points",
    "output_topic": "/lidar/points_mast_base_link",
    "target_frame": "mast_base_link",
    # How long to wait for a transform before dropping a cloud, in seconds.
    "tf_timeout_sec": 0.1,
    # If true, subscribe with the sensor-data QoS (best effort, small
    # history) which matches typical LiDAR / camera driver output.
    "use_sensor_data_qos": True,
}


class FrameTransformNode(Node):

    def __init__(self):
        super().__init__("frame_transform_node")

        self._declare_parameters()
        self._load_parameters()

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)

        qos = qos_profile_sensor_data if self.use_sensor_data_qos else 10

        self.sub = self.create_subscription(
            PointCloud2,
            self.input_topic,
            self.cloud_callback,
            qos,
        )

        self.pub = self.create_publisher(
            PointCloud2,
            self.output_topic,
            10,
        )

        self.get_logger().info(
            f"frame_transform_node: {self.input_topic} -> {self.output_topic} "
            f"(target_frame={self.target_frame})"
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def cloud_callback(self, msg: PointCloud2):
        source_frame = msg.header.frame_id

        if source_frame == self.target_frame:
            # Already in the target frame (e.g. running against recorded
            # data that was pre-transformed). Pass through unchanged.
            self.pub.publish(msg)
            return

        try:
            transform = self.tf_buffer.lookup_transform(
                self.target_frame,
                source_frame,
                msg.header.stamp,
                timeout=rclpy.duration.Duration(
                    seconds=self.tf_timeout_sec
                ),
            )
        except (
            tf2_ros.LookupException,
            tf2_ros.ConnectivityException,
            tf2_ros.ExtrapolationException,
        ) as exc:
            self.get_logger().warn(
                f"No transform {source_frame} -> {self.target_frame} yet: "
                f"{exc}. Dropping this cloud (static TF not published?).",
                throttle_duration_sec=5.0,
            )
            return

        try:
            transformed = do_transform_cloud(msg, transform)
        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"do_transform_cloud failed: {exc}")
            return

        transformed.header.frame_id = self.target_frame
        transformed.header.stamp = msg.header.stamp
        self.pub.publish(transformed)


def main(args=None):
    rclpy.init(args=args)

    node = FrameTransformNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
