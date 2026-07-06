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

On tf_timeout_sec: the target frame (mast_base_link) is dynamic, broadcast
by mast_pose_node at its own publish_rate_hz (default 20 Hz -> a new sample
every 50 ms). A lookup for an exact past timestamp can only succeed once a
TF sample *newer* than that timestamp has arrived (tf2 interpolates between
two known samples, it never extrapolates into the future). If a sensor's
cloud timestamp lands in the ~50 ms gap right after the last broadcast, the
lookup has to wait for the *next* broadcast before it can succeed -- so
tf_timeout_sec needs to comfortably cover that gap (plus jitter/scheduling
slack), not just be "some small number". 0.1s cut it too close in practice
(see chat: ExtrapolationException on the lidar branch); 0.3s gives roughly
6x the nominal 50 ms period of margin.

On concurrency (MultiThreadedExecutor, not TransformListener(spin_thread=True)):
without some form of concurrency, the listener's own /tf and /tf_static
subscriptions run on the *same* single-threaded executor as cloud_callback.
If cloud_callback is blocked inside lookup_transform's timeout wait for a
not-yet-arrived transform, the executor can't process any other callback
either -- including the very /tf message that would satisfy the wait. That
message just queues up and gets handled only after cloud_callback already
gave up. Net effect: raising tf_timeout_sec alone does nothing, because the
wait can never be resolved early by new data.

We first tried fixing this with `TransformListener(..., spin_thread=True)`,
which gives the listener its own background thread -- but that thread runs
its own separate executor with the *same node* added to it, while main()
also spins that node via the normal single-threaded rclpy.spin(). The same
node ends up added to two executors at once, which is unsupported and
produced exactly the symptom we were chasing: the buffer's most-recent
transform stayed stale for the entire timeout window instead of updating
every ~50ms as mast_pose_node published.

The correct fix: run this node under a single `MultiThreadedExecutor` (see
main() below) instead, and leave TransformListener at its default
(spin_thread=False). One executor, multiple worker threads, one node -- the
/tf subscription callback and cloud_callback can now genuinely run
concurrently, so a lookup_transform() wait in one thread doesn't block the
other thread from processing the next /tf message that would satisfy it.
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
    # See module docstring -- must comfortably exceed mast_pose_node's
    # broadcast period (1/publish_rate_hz), not just be "small".
    "tf_timeout_sec": 0.3,
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
        # Default (spin_thread=False) -- concurrency is handled by running
        # this whole node under a MultiThreadedExecutor in main() instead.
        # See module docstring for why spin_thread=True was tried and
        # reverted.
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

    # MultiThreadedExecutor, not the default rclpy.spin(node) -- see module
    # docstring. 2 threads is enough: one for cloud_callback (which may be
    # blocked inside a lookup_transform timeout wait), one free to run the
    # TransformListener's /tf and /tf_static subscription callbacks so a
    # new transform arriving can actually resolve that wait.
    executor = rclpy.executors.MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
