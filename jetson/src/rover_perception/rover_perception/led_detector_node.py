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
  2. Merge nearby same-blob fragments (2026-09, see "Fragment merging"
     below) BEFORE connected-component labeling, so a single physical LED
     that happens to split into several disconnected bright regions (lens
     blur gaps, internal LED structure, sensor noise near a saturated
     source) is still counted as one detection.
  3. `scipy.ndimage.label` to find connected components ("blobs") in the
     (merged) mask.
  4. Drop blobs outside [min_blob_area_px, max_blob_area_px] -- filters out
     both single-pixel sensor noise and large overexposed regions that
     aren't small, point-like LEDs. Area is still measured from the
     original (unmerged) bright-pixel mask, not the dilated one used for
     merging -- see below.
  5. Drop blobs whose color isn't "pure enough" to be one of this pattern's
     colors (currently blue/red -- see position_rover_node). Rather than
     matching each blob against fixed target RGB triples, this finds each
     blob's *dominant* channel (R, G or B -- whichever is highest) and
     checks it exceeds the second-highest by at least min_color_dominance.
     This is deliberately a *dominance* check rather than a fixed-RGB
     match: exposure and a camera's automatic white balance shift the
     exact RGB values a lot more than the "which channel wins"
     relationship, especially outdoors/indoors under different lighting.
     Toggle via enable_color_filter if this ever needs debugging. Which LED
     a detection corresponds to is *not* decided here -- this node just
     reports each blob's mean color (color_r/g/b); position_rover_node is
     the one that groups detections by dominant channel and solves the
     pattern's geometry (see its module docstring).
  6. For each surviving blob: pixel centroid, mean color (color_r/g/b --
     used both to double-check the dominance filter and by
     position_rover_node to classify which LED a detection belongs to),
     and a bearing vector from the camera intrinsics (pinhole
     back-projection, same math family as stereo_pointcloud_node -- just
     normalized to unit length since there's no depth here).

Indoor/lit-room testing note (2026-09): a brightly lit test environment
produces far more false-positive blobs than dark/field conditions --
warm-white room lighting is often already red-dominant enough to clear
min_color_dominance, and reflections off bright/glossy surfaces clear
brightness_threshold easily. Since position_rover_node requires an *exact*
color-count match (see its module docstring), any extra spurious detection
of either color causes every frame to be dropped. If testing somewhere
brightly lit, raising brightness_threshold and min_color_dominance well
above the defaults (which were tuned against the old fake camera's clean
synthetic background, not real ambient light) is expected to be necessary
-- tune empirically by comparing the color_r/g/b of known-real LED
detections against the color_r/g/b of the false positives you're seeing.

Fragment merging (added 2026-09)
-----------------------------------------------------------------------------
Real LEDs sometimes show up as *multiple* separate blobs instead of one --
e.g. a bright core plus a couple of satellite fragments just outside it
(lens blur/blooming, a few pixels dipping below brightness_threshold in the
middle of the LED's footprint, sensor noise right at the edge of a
saturated region). Left alone, this breaks position_rover_node exactly like
extra ambient-light false positives do: it needs an exact color count (see
its module docstring), and one physical LED reported as 2-3 detections
throws that count off just as badly as genuine noise would.

Fix: dilate the brightness mask by merge_dilation_px pixels *before*
connected-component labeling (scipy.ndimage.binary_dilation), so nearby
fragments become one connected region and get one label. Area, centroid,
and color are still computed from the ORIGINAL (undilated) bright-pixel
mask, restricted to each now-merged label -- the dilation only changes
which fragments count as "the same blob", it does not inflate the
measured size/color of that blob with the dark gap pixels used to bridge
the fragments (those contribute zero weight, since they're not part of the
original mask).

Tuning trade-off, worth understanding before changing merge_dilation_px:
too small and it won't bridge a real LED's own internal fragmentation
(back to the original problem); too large and it starts merging
*genuinely separate* nearby LEDs into a single blob instead (a different,
arguably worse problem -- position_rover_node would then see too few
detections of that color instead of too many, still breaking the exact-
count check, but now also silently discarding real position information).
Pick merge_dilation_px well below half the smallest expected pixel
separation between two distinct LEDs at your typical operating distance --
check this against your own footage (compare the pixel gap between
fragments of one LED against the pixel gap between two different LEDs).
Default (2px) is deliberately conservative; raise it a little if fragments
still aren't merging, but verify with real detections that distinct LEDs
aren't merging into each other first.

Overexposed white LED cores (added 2026-09)
-----------------------------------------------------------------------------
A bright LED often saturates to a near-white core (e.g. 255,250,252) with
only its rim still clearly colored (e.g. 40,70,250 for blue). Averaging
color over the whole blob drags the mean towards white and can push the
dominance below min_color_dominance, so the real LED gets rejected while
small, detached, purely colored rim fragments pass. Fix: the blob's color
is computed only from pixels whose SMALLEST channel is below
white_min_channel (i.e. not white); area and centroid still use all bright
pixels. Blobs without any colored pixels (pure white -- lamps, glare) are
dropped when the color filter is enabled. This complements, not replaces,
a short fixed camera exposure.
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
from rover_control_msgs.msg import OperationalModeSettings


DEFAULTS = {
    "image_topic": "/mono_cam/image_raw",
    "camera_info_topic": "/mono_cam/camera_info",
    "detections_topic": "/mono_cam/led_detections",
    "state_topic": "/operational_mode/settings",

    # A pixel counts as "LED" if its brightest channel is >= this. Tuned
    # against the old fake camera's clean synthetic background -- raise
    # substantially for real, especially lit-room, testing (see module
    # docstring's "Indoor/lit-room testing note").
    "brightness_threshold": 150,

    # Connected-component size filter, in pixels. Measured from the
    # original (undilated) bright-pixel mask -- unaffected by
    # merge_dilation_px below.
    "min_blob_area_px": 2,
    "max_blob_area_px": 4000,

    # Fragment merging -- see module docstring "Fragment merging" section.
    # 0 disables merging (old behavior: every connected bright region in
    # the raw mask is its own blob).
    "merge_dilation_px": 4,

    # Color filter: this pattern's LEDs are solid primary colors (blue/red
    # -- see position_rover_node). A blob's single brightest channel
    # (whichever of R/G/B is highest) must exceed the second-highest by at
    # least this much (0-255 scale) to count as a real detection -- this
    # accepts red- or blue-dominant blobs alike and rejects washed-out/
    # white/gray ones (including most ambient lighting/reflections). Set
    # enable_color_filter to False to fall back to brightness+size only
    # (e.g. while debugging). Tuned against the old fake camera -- raise
    # substantially for real, especially lit-room, testing (see module
    # docstring).
    "enable_color_filter": True,
    "min_color_dominance": 80,

    # Pixels whose SMALLEST channel is >= this count as white (overexposed
    # LED core) and are ignored when computing a blob's color. Area and
    # centroid still use them. See module docstring "Overexposed white LED
    # cores".
    "white_min_channel": 200,

    "sync_slop_sec": 0.05,
}


class LedDetectorNode(Node):

    def __init__(self):
        super().__init__("led_detector_node")

        self._declare_parameters()
        self._load_parameters()
        self.state = "STANDBY"

        self.image_sub = None
        self.info_sub = None
        self.sync = None
        self.detections_pub = None

        self.state_sub = self.create_subscription(
            OperationalModeSettings,
            self.state_topic,
            self.state_callback,
            10,
        )

    def state_callback(self, msg):
        self.state = msg.mono_cam

        if self.state in ("OFF"):
            self.get_logger().info("led_detector_node: STANDBY/OFF")

            self.destroy_subscription(self.image_sub.sub)
            self.destroy_subscription(self.info_sub.sub)
            self.destroy_publisher(self.detections_pub)

            self.image_sub = None
            self.info_sub = None
            self.sync = None
            self.detections_pub = None

        elif self.state == "ON":
            self.get_logger().info("led_detector_node: ON")

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

            self.detections_pub = self.create_publisher(
                LedDetectionArray,
                self.detections_topic,
                10,
            )

            self.get_logger().info(
                f"led_detector_node: {self.image_topic} + "
                f"{self.camera_info_topic} -> {self.detections_topic} "
                f"(brightness>={self.brightness_threshold}, "
                f"area in [{self.min_blob_area_px}, {self.max_blob_area_px}] px, "
                f"merge_dilation_px={self.merge_dilation_px}, "
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

            # Fragment merging -- see module docstring. Labeling runs on the
            # (optionally dilated) mask, but area/centroid/color below are
            # always computed from the ORIGINAL mask, so merging only
            # changes which fragments count as one blob, never what that
            # blob's measured size/position/color is.
            if self.merge_dilation_px > 0:
                label_mask = ndimage.binary_dilation(
                    mask, iterations=self.merge_dilation_px
                )
            else:
                label_mask = mask

            labels, num_labels = ndimage.label(label_mask)

            if num_labels > 0:
                fx, fy = info_msg.k[0], info_msg.k[4]
                cx, cy = info_msg.k[2], info_msg.k[5]

                label_ids = np.arange(1, num_labels + 1)
                areas = ndimage.sum(mask, labels, label_ids)
                centroids = ndimage.center_of_mass(mask, labels, label_ids)

                # Color from colored pixels only -- see module docstring
                # "Overexposed white LED cores". Saturated near-white core
                # pixels (smallest channel >= white_min_channel) would
                # otherwise drag the mean towards white. Still mask-weighted
                # (dark gap pixels from fragment merging contribute zero),
                # but now divided by the number of COLORED bright pixels
                # per blob instead of all bright pixels.
                color_mask = mask & (frame.min(axis=2) < self.white_min_channel)
                color_counts = ndimage.sum(color_mask, labels, label_ids)
                safe_counts = np.maximum(color_counts, 1.0)

                masked_r = np.where(color_mask, frame[:, :, 0].astype(np.float64), 0.0)
                masked_g = np.where(color_mask, frame[:, :, 1].astype(np.float64), 0.0)
                masked_b = np.where(color_mask, frame[:, :, 2].astype(np.float64), 0.0)
                mean_r = ndimage.sum(masked_r, labels, label_ids) / safe_counts
                mean_g = ndimage.sum(masked_g, labels, label_ids) / safe_counts
                mean_b = ndimage.sum(masked_b, labels, label_ids) / safe_counts

                for i, area in enumerate(areas):
                    area = int(area)

                    if area < self.min_blob_area_px or area > self.max_blob_area_px:
                        continue

                    # Pure white blob (no colored pixels at all) -> lamp,
                    # glare or similar, not a colored LED.
                    if self.enable_color_filter and color_counts[i] < 3:
                        continue

                    if self.enable_color_filter:
                        # Dominant channel minus the *second*-highest
                        # channel (not the sum of the other two) -- e.g.
                        # pure blue (60,60,255) must still pass even though
                        # R+G=120 isn't small compared to B=255.
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