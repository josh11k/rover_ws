"""Combine per-wedge raw point cloud snapshots into one global scan.

Companion to ground_segmentation_node's multi-wedge scanning feature (see
that file's module docstring, "Multi-wedge scanning" section) -- this is
the small, dedicated node mentioned there that runs *after* all wedges of
one scan session have been saved.

Why a separate node instead of doing this inside ground_segmentation_node
---------------------------------------------------------------------------
Keeps responsibilities cleanly split: ground_segmentation_node only ever
knows about "buffer what arrives on global_points, dump on request,
classify on request" -- it has no idea wedges exist as a concept, doesn't
read from disk, and doesn't know how many wedges a session has. This node
is the only place that knows about the wedge *files* themselves.

What it does (one Trigger service call, combine_wedges)
-----------------------------------------------------------
  1. glob() every wedge_*.npz currently in wedge_dir (no count needs to be
     known or passed in -- however many files exist get combined).
  2. Load and concatenate their raw point arrays into one big (N,4) array.
     No orientation/transform math needed: wedge files were already saved
     in mast_base_link (the pan/tilt-invariant frame) at buffer time by
     ground_segmentation_node, specifically so that different wedges
     combine via plain concatenation -- see the project's earlier
     mast_base_link design discussion.
  3. Publish the combined cloud, once, to output_topic -- this must match
     ground_segmentation_node's input_topic (both default to
     /perception/global_points) so it lands in the same place a normal
     fused-cloud message would, and gets buffered by
     ground_segmentation_node's cloud_callback exactly like any other
     message (see that file's docstring: buffering only, no classification
     yet at this point).
  4. Wait post_publish_delay_sec, then call ground_segmentation_node's
     finalize_ground_segmentation service, which classifies everything
     just buffered (the whole combined scan, since it arrived in one
     message) and publishes ground_points/obstacle_points once, which
     obstacle_grid_node then grids and saves as usual.

Why a blind delay instead of some kind of acknowledgement
-------------------------------------------------------------
There's no built-in "the subscriber has finished processing" signal for a
plain topic publish. Rather than build one, this leans on the same
"one-time, non-real-time-critical" framing used throughout the wedge/scan
design (see ground_segmentation_node's docstring): a generous fixed delay
(default 2s) is simple, easy to reason about, and cheap to make more
generous if the combined cloud turns out to be large enough that buffering
it takes noticeably longer than that on the Jetson. If this ever proves too
short, raise post_publish_delay_sec -- there's no benefit to a slower
combined-cloud buffering pass, so erring generous costs nothing here.

Why a ReentrantCallbackGroup + MultiThreadedExecutor
---------------------------------------------------------
combine_wedges (this node's own service handler) calls out to another
service (finalize_ground_segmentation) and blocks waiting for the
response. In a single-threaded executor that would deadlock -- the
response callback for the outgoing call could never run while the
incoming service callback that's waiting for it is still occupying the
only thread. Two threads (one for combine_wedges' handler, one free for
finalize_ground_segmentation's response) is the minimum needed; see
main() and frame_transform_node.py for the same pattern.

Wedge files are NOT deleted by this node
---------------------------------------------
Deliberately left alone after combining, for two reasons: (1) lets you
inspect/debug them after a run if something looks wrong, (2) keeps "when
does a wedge session's data actually go away" a single, explicit action --
ground_segmentation_node's clear_wedge_session service, called once at the
start of the *next* session -- rather than splitting that responsibility
across two nodes and risking them disagreeing about it.

Not yet wired into command_node's orchestration
-----------------------------------------------------
combine_wedges is meant to be called once, by command_node, right after
the last "perception OFF" of a wedge-rotation sequence (and after turning
perception back ON one more time so ground_segmentation_node has an empty,
ready buffer -- see ground_segmentation_node's docstring). That
orchestration doesn't exist yet; this node only exposes the service.
"""

import glob
import os
import time

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from sensor_msgs.msg import PointCloud2
from std_msgs.msg import Header
from std_srvs.srv import Trigger

from rover_perception.pointcloud_filters import create_weighted_cloud


DEFAULTS = {
    # Must match ground_segmentation_node's wedge_save_dir.
    "wedge_dir": "/home/team/rover_maps/wedges",
    # Must match ground_segmentation_node's input_topic.
    "output_topic": "/perception/global_points",
    "finalize_service": "finalize_ground_segmentation",
    # Blind delay after publishing the combined cloud, before calling
    # finalize_ground_segmentation -- see module docstring.
    "post_publish_delay_sec": 2.0,
    # Applies both to waiting for finalize_ground_segmentation to become
    # available and to waiting for its response.
    "finalize_service_timeout_sec": 10.0,
    # Used only if every wedge file is somehow missing a frame_id (should
    # not normally happen -- ground_segmentation_node always writes one).
    "default_frame_id": "mast_base_link",
}


class WedgeCombinerNode(Node):

    def __init__(self):
        super().__init__("wedge_combiner_node")

        self._declare_parameters()
        self._load_parameters()

        # See module docstring "Why a ReentrantCallbackGroup +
        # MultiThreadedExecutor" section -- combine_wedges' handler blocks
        # on a call to another service, so it and that call's response
        # callback must be able to run on different threads.
        cb_group = ReentrantCallbackGroup()

        self.cloud_pub = self.create_publisher(
            PointCloud2, self.output_topic, 10,
        )

        self.finalize_client = self.create_client(
            Trigger, self.finalize_service, callback_group=cb_group,
        )

        self.combine_srv = self.create_service(
            Trigger, "combine_wedges", self._combine_callback,
            callback_group=cb_group,
        )

        self.get_logger().info(
            f"wedge_combiner_node ready. wedge_dir={self.wedge_dir}, "
            f"output_topic={self.output_topic}. Call the combine_wedges "
            f"service once all wedges of a session have been saved (and "
            f"ground_segmentation_node is ON with a fresh buffer)."
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def _combine_callback(self, request, response):
        try:
            wedge_paths = sorted(
                glob.glob(os.path.join(self.wedge_dir, "wedge_*.npz"))
            )

            if not wedge_paths:
                response.success = False
                response.message = (
                    f"No wedge files found in {self.wedge_dir} -- nothing "
                    f"to combine. Did save_wedge_points get called during "
                    f"the scan?"
                )
                self.get_logger().warning(f"combine_wedges: {response.message}")
                return response

            all_points = []
            frame_ids = set()

            for path in wedge_paths:
                try:
                    data = np.load(path, allow_pickle=True)
                    pts = data["points"]
                    if pts.size == 0:
                        continue
                    all_points.append(pts)
                    frame_ids.add(str(data["frame_id"]))
                except Exception as exc:  # noqa: BLE001 - skip, don't abort the whole combine
                    self.get_logger().warning(
                        f"combine_wedges: skipping unreadable wedge file "
                        f"{path}: {exc}"
                    )

            if not all_points:
                response.success = False
                response.message = (
                    f"Found {len(wedge_paths)} wedge file(s) in "
                    f"{self.wedge_dir} but none contained usable points."
                )
                self.get_logger().warning(f"combine_wedges: {response.message}")
                return response

            if len(frame_ids) > 1:
                self.get_logger().warning(
                    f"combine_wedges: wedge files disagree on frame_id "
                    f"({sorted(frame_ids)}) -- combining anyway, since "
                    f"points are expected to already be in the shared "
                    f"pan/tilt-invariant frame (mast_base_link) regardless "
                    f"of which wedge they came from. Worth checking this "
                    f"is expected."
                )

            frame_id = next(iter(frame_ids)) if frame_ids else self.default_frame_id

            combined = np.concatenate(all_points, axis=0).astype(np.float32)

            header = Header()
            header.stamp = self.get_clock().now().to_msg()
            header.frame_id = frame_id

            self.cloud_pub.publish(create_weighted_cloud(header, combined))

            self.get_logger().info(
                f"combine_wedges: published {len(combined)} combined points "
                f"from {len(wedge_paths)} wedge file(s) to "
                f"{self.output_topic} (frame_id={frame_id}). Waiting "
                f"{self.post_publish_delay_sec}s before finalizing..."
            )

            # Blind delay -- see module docstring "Why a blind delay"
            # section. Blocks only this callback's thread; the
            # ReentrantCallbackGroup + MultiThreadedExecutor (see main())
            # keep the rest of the node responsive in the meantime.
            time.sleep(self.post_publish_delay_sec)

            if not self.finalize_client.wait_for_service(
                timeout_sec=self.finalize_service_timeout_sec
            ):
                response.success = False
                response.message = (
                    f"Published {len(combined)} combined points, but "
                    f"{self.finalize_service} did not become available "
                    f"within {self.finalize_service_timeout_sec}s -- is "
                    f"ground_segmentation_node running and turned ON? Call "
                    f"{self.finalize_service} manually once it's up."
                )
                self.get_logger().error(f"combine_wedges: {response.message}")
                return response

            future = self.finalize_client.call_async(Trigger.Request())

            wait_start = time.time()
            while not future.done():
                if time.time() - wait_start > self.finalize_service_timeout_sec:
                    response.success = False
                    response.message = (
                        f"Published {len(combined)} combined points, but "
                        f"the {self.finalize_service} call timed out after "
                        f"{self.finalize_service_timeout_sec}s."
                    )
                    self.get_logger().error(f"combine_wedges: {response.message}")
                    return response
                time.sleep(0.05)

            finalize_result = future.result()

            response.success = bool(finalize_result.success)
            response.message = (
                f"Combined {len(combined)} points from {len(wedge_paths)} "
                f"wedge file(s) and published to {self.output_topic}. "
                f"{self.finalize_service} reported: {finalize_result.message}"
            )

            if response.success:
                self.get_logger().info(f"combine_wedges: {response.message}")
            else:
                self.get_logger().error(f"combine_wedges: {response.message}")

        except Exception as exc:  # noqa: BLE001 - report, don't crash
            response.success = False
            response.message = f"combine_wedges failed: {exc}"
            self.get_logger().error(response.message)

        return response


def main(args=None):
    rclpy.init(args=args)

    node = WedgeCombinerNode()

    # 2 threads minimum -- see module docstring "Why a ReentrantCallbackGroup
    # + MultiThreadedExecutor" section.
    executor = MultiThreadedExecutor(num_threads=2)
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
