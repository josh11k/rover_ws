"""Merge the (already transformed + filtered) lidar and stereo clouds.

This is the diagram's "make_global_pointcloud_node" ("combine stereocam and
lidar point cloud into one"). By the time clouds reach this node they have
already been:

  1. transformed into mast_base_link (the mast's own quasi-static frame --
     only moves under real mast lean, not with pan/tilt) by
     frame_transform_node, and
  2. cropped / downsampled / outlier-filtered by pointcloud_preprocessing_node
     (which also guarantees both clouds carry a 4th "weight" field by now,
     see pointcloud_filters.py)

so this node's job is just concatenation, not another round of
sensor-specific processing. The per-point weight is passed through
unchanged -- it's consumed downstream by terrain_analysis.py.

Why this is *not* a message_filters.ApproximateTimeSynchronizer anymore
-------------------------------------------------------------------------
The original implementation paired up lidar+stereo clouds with an
ApproximateTimeSynchronizer, which only calls back once it has a matching
sample from *every* registered topic within `slop` of each other. In
practice (see chat) this turned out to be fragile in exactly the way that
matters most: if either sensor branch stalls or lags for a few seconds
(system under load, a sensor temporarily silent, timer jitter under a busy
executor -- all things we actually observed), the synchronizer simply never
fires, and the *entire* fused output goes silent, even though the other
sensor was working fine the whole time. A single flaky sensor shouldn't be
able to veto the whole terrain map.

The replacement (same "cache latest + timer" pattern mast_pose_node already
uses, for consistency): each sensor topic is subscribed independently and
just overwrites a "latest message" cache. A timer, running at
publish_rate_hz independent of either sensor's own rate, periodically
builds one fused cloud from whatever is currently cached -- lidar only,
stereo only, or both -- as long as each cached message isn't older than
max_input_age_sec (a message older than that is treated as "no data from
that sensor right now", so we don't keep fusing in ancient, meaningless
points forever if a sensor actually dies).

Trade-off, stated plainly: we give up the guarantee that fused points came
from sensors observing at *the same instant* (to within a tight slop) --
lidar and stereo contributions to one published cloud can now be up to
max_input_age_sec apart in capture time. For a quasi-static mast building up
a terrain map over many pan positions, that's an acceptable trade for "the
pipeline never goes fully silent because one sensor hiccupped".
"""

import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import PointCloud2

from rover_perception.pointcloud_filters import (
    create_weighted_cloud,
    read_weighted_points,
)


DEFAULTS = {
    "lidar_points_topic": "/lidar/points_filtered",
    "stereo_points_topic": "/stereo/points_filtered",
    "output_topic": "/perception/global_points",
    "output_frame_id": "mast_base_link",
    # Independent of either sensor's own publish rate -- see module
    # docstring. Fires periodically and fuses whatever is currently cached.
    "publish_rate_hz": 10.0,
    # A cached message older than this is treated as "that sensor has no
    # current data" rather than being fused in as stale/misleading input.
    "max_input_age_sec": 2.0,
}


class GlobalPointcloudFusionNode(Node):

    def __init__(self):
        super().__init__("global_pointcloud_fusion_node")

        self._declare_parameters()
        self._load_parameters()

        self.pub = self.create_publisher(
            PointCloud2,
            self.output_topic,
            10,
        )

        # Independent subscribers -- no message_filters, no requirement that
        # both fire together. Each just remembers the latest message.
        self._latest_lidar = None
        self._latest_stereo = None

        self.lidar_sub = self.create_subscription(
            PointCloud2,
            self.lidar_points_topic,
            self._lidar_callback,
            10,
        )
        self.stereo_sub = self.create_subscription(
            PointCloud2,
            self.stereo_points_topic,
            self._stereo_callback,
            10,
        )

        period = 1.0 / self.publish_rate_hz
        self.timer = self.create_timer(period, self._publish_fused)

        self.get_logger().info(
            f"global_pointcloud_fusion_node: {self.lidar_points_topic} + "
            f"{self.stereo_points_topic} -> {self.output_topic} "
            f"(independent cache + {self.publish_rate_hz}Hz timer, "
            f"max_input_age_sec={self.max_input_age_sec})"
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def _lidar_callback(self, msg: PointCloud2):
        self._latest_lidar = msg

    def _stereo_callback(self, msg: PointCloud2):
        self._latest_stereo = msg

    def _fresh_or_none(self, msg):
        """Return msg if it exists and isn't older than max_input_age_sec,
        else None -- i.e. "no current data from that sensor".
        """
        if msg is None:
            return None

        now = self.get_clock().now()
        msg_time = rclpy.time.Time.from_msg(msg.header.stamp)
        age_sec = (now - msg_time).nanoseconds / 1e9

        if age_sec > self.max_input_age_sec:
            return None

        return msg

    def _publish_fused(self):
        try:
            lidar_msg = self._fresh_or_none(self._latest_lidar)
            stereo_msg = self._fresh_or_none(self._latest_stereo)

            if lidar_msg is None and stereo_msg is None:
                # Neither sensor has current data -- nothing to publish,
                # but the node itself stays alive and keeps trying every
                # timer tick (unlike the old synchronizer, which would just
                # silently never fire again until both sides recovered).
                return

            arrays = []
            newest_header = None
            newest_stamp = -1.0

            for msg in (lidar_msg, stereo_msg):
                if msg is None:
                    continue

                points = read_weighted_points(msg)
                if points.size > 0:
                    arrays.append(points)

                stamp = (
                    msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
                )
                if stamp > newest_stamp:
                    newest_stamp = stamp
                    newest_header = msg.header

            if not arrays:
                return

            combined = arrays[0] if len(arrays) == 1 else np.concatenate(
                arrays, axis=0
            )

            newest_header.frame_id = self.output_frame_id
            out_msg = create_weighted_cloud(newest_header, combined)
            self.pub.publish(out_msg)

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"_publish_fused failed: {exc}")


def main(args=None):
    rclpy.init(args=args)

    node = GlobalPointcloudFusionNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
