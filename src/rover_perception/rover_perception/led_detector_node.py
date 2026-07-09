"""Find LED blobs (other robots) in the mono-camera image.

This is the diagram's "led_detector_node", the second stage of the LED
branch (mono_cam_node -> led_detector_node -> position_rover_node). It does
not compute a position itself -- a single camera only gives a *direction*
to each blob, not a distance. That's why this node's output is a bearing
(unit direction vector) per detection, not a pose; turning bearings into
actual positions (e.g. via known LED spacing, or triangulating across
multiple frames as the rover moves) is position_rover_node's job, not
this one's.

Algorithm (deliberately simple, no OpenCV/cv_bridge dependency -- reuses
scipy, which the workspace already depends on everywhere else):

  1. Threshold on per-pixel brightness (max of R/G/B) -> binary mask.
  2. `scipy.ndimage.label` to find connected components ("blobs") in that
     mask.
  3. Drop blobs outside [min_blob_area_px, max_blob_area_px] -- filters out
     both single-pixel sensor noise and large overexposed regions that
     aren't small, point-like LEDs.
  4. Drop blobs whose color isn't "pure enough" to be one of the rover's 3
     LED panels (roof=green, left=red, right=blue -- see
     fake_mono_camera_node). Rather than matching each blob against 3 fixed
     target RGB triples, this finds each blob's *dominant* channel (R, G or
     B -- whichever is highest) and checks it exceeds the other two by at
     least min_color_dominance. A blob that passes is, by construction, one
     of exactly 3 colors -- dominant-red, dominant-green or dominant-blue --
     which is exactly the 3-panel-color scheme downstream nodes expect. This
     is deliberately a *dominance* check rather than a fixed-RGB match:
     exposure and a camera's automatic white balance shift the exact RGB
     values a lot more than the "which channel wins" relationship,
     especially outdoors. Toggle via enable_color_filter if this ever needs
     debugging. Which panel a detection belongs to is *not* decided here --
     this node just reports each blob's mean color (color_r/g/b);
     position_rover_node is the one that groups detections by dominant
     channel into roof/left/right and solves each panel's geometry
     independently (see its module docstring).
  5. For each surviving blob: pixel centroid, mean color (color_r/g/b --
     used both to double-check the dominance filter and by
     position_rover_node to classify which panel a detection belongs to),
     and a bearing vector from the camera intrinsics (pinhole
     back-projection, same math family as stereo_pointcloud_node -- just
     normalized to unit length since there's no depth here).

Runs against the fake camera today unchanged: fake_mono_camera_node draws
green/red/blue blobs (its 3 panel colors -- see its panel_*_color_*
parameters) on a dark noisy background, so this node's thresholding +
color-filter logic is already exercised end-to-end without real hardware.
"""

import math

import numpy as np
from scipy import ndimage

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from sensor_msgs.msg import Image, CameraInfo

import message_filters

from rover_perception_msgs.msg import LedDetection, LedDetectionArray


DEFAULTS = {
    "image_topic": "/mono_cam/image_raw",
    "camera_info_topic": "/mono_cam/camera_info",
    "detections_topic": "/mono_cam/led_detections",

    # A pixel counts as "LED" if its brightest channel is >= this.
    "brightness_threshold": 180,

    # Connected-component size filter, in pixels.
    "min_blob_area_px": 4,
    "max_blob_area_px": 2000,

    # Color filter: the rover's 3 LED panels are each a solid primary color
    # (green/red/blue -- see fake_mono_camera_node). A blob's single
    # brightest channel (whichever of R/G/B is highest) must exceed the
    # other two by at least this much (0-255 scale) to count as a real
    # detection -- this accepts red-, green- or blue-dominant blobs alike
    # and rejects washed-out/white/gray ones. Set enable_color_filter to
    # False to fall back to brightness+size only (e.g. while debugging).
    "enable_color_filter": True,
    "min_color_dominance": 40,

    "sync_slop_sec": 0.05,
}


class LedDetectorNode(Node):

    def __init__(self):
        super().__init__("led_detector_node")

        self._declare_parameters()
        self._load_parameters()

        self.detections_pub = self.create_publisher(
            LedDetectionArray,
            self.detections_topic,
            10,
        )

        self.image_sub = message_filters.Subscriber(
            self, Image, self.image_topic, qos_profile=qos_profile_sensor_data
        )
        self.info_sub = message_filters.Subscriber(
            self, CameraInfo, self.camera_info_topic,
            qos_profile=qos_profile_sensor_data
        )

        self.sync = message_filters.ApproximateTimeSynchronizer(
            [self.image_sub, self.info_sub],
            queue_size=10,
            slop=self.sync_slop_sec,
        )
        self.sync.registerCallback(self.image_callback)

        self.get_logger().info(
            f"led_detector_node: {self.image_topic} + "
            f"{self.camera_info_topic} -> {self.detections_topic} "
            f"(brightness>={self.brightness_threshold}, "
            f"area in [{self.min_blob_area_px}, {self.max_blob_area_px}] px, "
            f"color_filter={self.enable_color_filter} "
            f"(color_dominance>={self.min_color_dominance}))"
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def image_callback(self, image_msg: Image, info_msg: CameraInfo):
        try:
            if image_msg.encoding != "rgb8":
                self.get_logger().warn(
                    f"Unexpected image encoding '{image_msg.encoding}', "
                    "expected rgb8. Skipping frame.",
                    throttle_duration_sec=5.0,
                )
                return

            frame = np.frombuffer(image_msg.data, dtype=np.uint8).reshape(
                image_msg.height, image_msg.width, 3
            )

            out_msg = LedDetectionArray()
            out_msg.header = image_msg.header

            mask = frame.max(axis=2) >= self.brightness_threshold
            labels, num_labels = ndimage.label(mask)

            if num_labels > 0:
                fx, fy = info_msg.k[0], info_msg.k[4]
                cx, cy = info_msg.k[2], info_msg.k[5]

                label_ids = np.arange(1, num_labels + 1)
                areas = ndimage.sum(mask, labels, label_ids)
                centroids = ndimage.center_of_mass(mask, labels, label_ids)

                mean_r = ndimage.mean(frame[:, :, 0], labels, label_ids)
                mean_g = ndimage.mean(frame[:, :, 1], labels, label_ids)
                mean_b = ndimage.mean(frame[:, :, 2], labels, label_ids)

                for i, area in enumerate(areas):
                    area = int(area)

                    if area < self.min_blob_area_px or area > self.max_blob_area_px:
                        continue

                    if self.enable_color_filter:
                        # Dominant channel minus the *second*-highest
                        # channel (not the sum of the other two) -- e.g.
                        # pure green (60,255,80) must still pass even
                        # though R+B=140 isn't small compared to G=255.
                        channels = sorted([mean_r[i], mean_g[i], mean_b[i]], reverse=True)
                        dominance = channels[0] - channels[1]
                        if dominance < self.min_color_dominance:
                            continue

                    row, col = centroids[i]
                    u, v = float(col), float(row)

                    # Pinhole back-projection to a unit bearing vector, same
                    # family of math as stereo_pointcloud_node -- just
                    # normalized, since a mono image has no depth to scale by.
                    ray_x = (u - cx) / fx
                    ray_y = (v - cy) / fy
                    norm = math.sqrt(ray_x * ray_x + ray_y * ray_y + 1.0)

                    detection = LedDetection()
                    detection.pixel_u = u
                    detection.pixel_v = v
                    detection.area_px = area
                    detection.color_r = int(np.clip(mean_r[i], 0, 255))
                    detection.color_g = int(np.clip(mean_g[i], 0, 255))
                    detection.color_b = int(np.clip(mean_b[i], 0, 255))
                    detection.bearing.x = ray_x / norm
                    detection.bearing.y = ray_y / norm
                    detection.bearing.z = 1.0 / norm

                    out_msg.detections.append(detection)

            self.detections_pub.publish(out_msg)

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"image_callback failed: {exc}")


def main(args=None):
    rclpy.init(args=args)

    node = LedDetectorNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
