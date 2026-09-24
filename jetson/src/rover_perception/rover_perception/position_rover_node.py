"""Solve the rover's pose (position + orientation) in the world frame from
led_detector_node's LED-blob detections -- the diagram's "position_rover_node",
the final consumer of the mono-cam/LED branch.

Physical setup (single LED pattern, 2026-09 redesign)
-----------------------------------------------------------------------------
For practical reasons the rover now carries a single, fixed LED pattern
(previously: 3 separate panels, roof/left/right -- that design is gone,
replaced entirely by this one). 4 LEDs, flat (all on one plane, z=0 in the
pattern's own local frame), coordinates as measured (origin = LED1, x = to
the right as drawn/laid out, y = up):

    LED1: x=0.0    mm, y=0.0   mm, blue   (pattern-local origin)
    LED2: x=32.6   mm, y=0.0   mm, blue
    LED3: x=50.3   mm, y=24.9  mm, red
    LED4: x=66.5   mm, y=0.0   mm, blue

This shape has no symmetry (LED1-LED2 spacing, 32.6mm, differs from
LED2-LED4 spacing, 33.9mm; LED3 sits off-center between LED2/LED4), so --
same as the old design -- a correct correspondence between detections and
model points has an unambiguously better fit than any wrong one.

Color-constrained correspondence search (replaces the old 24-permutation
exhaustive search)
-----------------------------------------------------------------------------
With 3 blue + 1 red LED, led_detector_node's per-blob dominant-color report
(color_r/g/b) already tells us almost the whole correspondence for free:
the single red detection can only be LED3 (the pattern's one red point) --
no search needed there. Only the 3 blue detections still need to be matched
against the 3 blue model points (LED1, LED2, LED4), which means only 3! = 6
candidate correspondences instead of the old 4! = 24 -- a real speedup
(this runs x4 yaw seeds per candidate in the pose solve below, so 24 solves
total instead of 96), and meaningfully less ambiguity risk, since color
already rules out 3/4 of the wrong pairings before any geometry is even
considered.

This is written generically (group detections by color, require the exact
count of each color the model has, permute only within each color group,
take the Cartesian product across colors) rather than hardcoded to
"3 blue + 1 red", so a future pattern with a different color layout doesn't
need this logic rewritten, just the LED_* DEFAULTS below changed.

Single mounting extrinsics (replaces the old per-panel roof/left/right
dict)
-----------------------------------------------------------------------------
Only one pattern now, so only one fixed mounting transform (rover-local
rotation + offset) is needed, not three. Values below come directly from
the chat discussion that pinned these down:

  - The pattern faces forward (pattern normal, i.e. the direction it's lit
    up toward, points in the rover's own direction of travel) -- confirmed
    via "wenn der Rover mir entgegen faehrt sehe ich genau die Draufsicht"
    (facing an oncoming rover, the observer sees exactly the schematic
    top-down layout above).
  - mount_offset (LED1, the pattern's local origin, relative to rover
    center): 10mm forward, 35mm left, 24mm up -- given directly in those
    terms by the user, so no forward/left/up ambiguity here.
  - Mirror effect, resolved explicitly rather than assumed: an object
    coming toward you has its own right appear on YOUR left (face someone
    walking toward you -- their right hand is on your left). This matters
    because the schematic above was drawn/measured as *seen*, and its
    "increasing x" direction (LED1 -> LED2 -> LED4) was confirmed
    physically -- sitting ON the rover facing forward, LED2 is on the
    RIGHT and LED4 is on the (far) LEFT. So the pattern's local +x axis
    (as drawn) maps to the rover's own LEFT direction, not right -- this
    is exactly the mirror effect, confirmed against physical placement
    instead of assumed from the camera-facing description alone.

Rover-local frame used here (internal to this file only -- see below):
x = forward, y = left, z = up (REP103-style). This only has to be
self-consistent between mount_offset and R_mount (both defined in these
same local axes) for the math to come out right; nothing external reads
this intermediate frame directly -- the published pose is always in
world_frame, via the TF lookup below.

Given all of that, in this file's (x=forward, y=left, z=up) rover-local
axes:
    normal    (pattern's local z, points toward the camera) = (1, 0, 0)  -- forward
    up_axis   (pattern's local y, toward LED3)               = (0, 0, 1)  -- up
    right_axis(pattern's local x, LED1->LED2->LED4 direction)= (0, 1, 0)  -- left (mirror effect)
    mount_offset = (0.010, 0.035, 0.024)  -- (forward, left, up), meters

This is a PnP problem (Perspective-n-Point): given known 3D points in the
pattern's own local frame and their observed bearing rays (unit vectors) in
the camera's optical frame, solve for the rigid transform (rotation +
translation) from pattern-local to camera-optical. led_detector_node gives
us bearings and a mean color per blob; it does NOT tell us *which* detected
blob is which specific LED -- that correspondence problem, plus turning the
solved pattern pose into a *rover* pose, is what this node does.

No OpenCV, consistent with led_detector_node's own from-scratch approach:

1. Classify each detection by its dominant color channel (color_r/g/b).
   Only "red" and "blue" are meaningful now (a stray "green"-dominant
   detection would be noise -- there's no green LED in this pattern -- and
   is dropped).

2. Require exactly 3 blue + 1 red detections this frame (derived from the
   model's own color list, not hardcoded -- see above). Fewer/more of
   either means a partial or ambiguous view; the frame is skipped rather
   than guessing.

3. Build all valid (color-constrained) correspondences -- 6 for this
   pattern -- and for each, solve the 6-DOF pose (rotation + translation,
   camera <- pattern) via nonlinear least squares (scipy.optimize.least_squares)
   minimizing the difference between predicted and observed unit bearings.
   A few different initial yaw guesses are tried per candidate purely to
   help the optimizer avoid bad local minima for large rotations -- cheap,
   since each solve only has 4 points.

4. Whichever (correspondence x yaw-seed) attempt converges to the lowest
   residual is kept. If even the best residual is too large
   (max_fit_residual_deg), the frame is dropped rather than publishing a
   bad pose.

5. The winning pose (camera <- pattern) is composed with the pattern's
   fixed mounting extrinsics (above) to get the pose of the *rover center*
   in the camera frame, camera <- rover.

6. That camera <- rover pose is transformed into the world frame using the
   existing TF tree (world -> mast_base_link -> mast_platform_link ->
   mono_cam_optical_frame, built by mast_pose_node + the static camera-mount
   transform) and published as a standard geometry_msgs/PoseStamped, plus
   broadcast as a TF (world -> rover_frame) so it shows up in RViz2 like
   everything else in this project.

Not yet updated to match: fake_mono_camera_node.py still simulates the OLD
3-panel roof/left/right pattern -- if you rely on that node for testing
without real hardware, it needs a matching rewrite to render this single
pattern instead, or simulated detections won't match what this node now
expects. Not done here -- flagged for a follow-up pass.

Active pan/tilt search + centering (added 2026-09, unchanged by the
single-pattern redesign)
-----------------------------------------------------------------------------
Since the mono camera has a limited field of view, this node also actively
points the mast's pan/tilt motors to find and keep the LED pattern
centered, rather than passively hoping it stays in frame. This is
deliberately here (not in led_detector_node) because led_detector_node only
reports raw color blobs per frame -- it has no idea whether a blob is
actually part of a validated, geometrically-consistent pattern or just
noise (a reflection, another light source). This node already does that
validation (the fit above), so it's the right place to decide "do we
actually see the pattern or not".

State machine, per detections_callback invocation:

- SEARCHING (self._tracking == False): pan sweeps across the full reachable
  range (pan_raw_min..pan_raw_max) in search_step_deg increments, tilt held
  fixed at tilt_home_raw. At each step: wait (via /motor_position/current
  feedback, with a frame-count timeout fallback) until the pan motor
  actually arrives, then watch for up to search_dwell_frames camera frames.
  If search_confirm_frames *consecutive* frames report a valid fit, declare
  it found and switch to TRACKING. Otherwise move to the next step. If the
  whole sweep completes with nothing found, log an error and park (still
  passively listening -- a lucky later detection still catches).

- TRACKING (self._tracking == True): every frame with a valid fit, the
  pattern's mean bearing vector gives a pan/tilt deviation from "dead
  ahead" (atan2 of the bearing's x/y against its z, i.e. directly against
  the camera's own optical axis -- no separate CameraInfo needed, the
  bearing already encodes it). If a deviation exceeds pan_deadband_deg /
  tilt_deadband_deg (each axis independent), a correction is requested for
  that axis via /motor_position/new. If lost_confirm_frames *consecutive*
  frames report no valid fit, the pattern is considered lost and a new
  search starts.

Dead-zone handling: the pan motor (Dynamixel AX-12A) can only reach 0..300
deg (raw 0..1023) in Joint Mode -- 300-360 deg is mechanically invalid, a
~60 deg gap it can never reach. If a requested correction would land outside
[pan_raw_min, pan_raw_max] (analogously for tilt, a *different* motor model
with its own, separately calibrated range), that axis is deliberately NOT
corrected -- it holds its current position and lets the pattern drift out of
frame rather than trying to chase it into an unreachable angle. Once the
pattern is then lost (lost_confirm_frames of nothing), the next search
starts from the OPPOSITE edge of the reachable range from wherever the pan
axis was blocked, on the assumption that whatever it was tracking kept
moving in that direction and will reappear on the far side of the gap
first. Tilt has no search of its own (only pan sweeps; tilt is assumed
roughly constant height), so only pan's block direction matters for where
the next search resumes.

MotorPosition (rover_control_msgs/msg/MotorPosition) is a full 5-motor
*absolute* command, not a per-motor delta (see stm_bridge_node_V2.py) --
motor1=tilt, motor5=pan, motor2/3/4=drive/other. Every command this node
sends echoes back the other three motors' last known real values from
/motor_position/current untouched, so a pan/tilt correction never
accidentally stomps on whatever the drive motors were doing.

pan_correction_sign/tilt_correction_sign exist because the real physical
direction (does increasing raw actually move toward where the pattern
drifted, or away?) hasn't been confirmed against real hardware yet -- flip
to -1 for either axis if the first live test moves the wrong way.

Not yet wired to any mode arbitration: this runs whenever mono_cam is ON,
with no awareness of e.g. an in-progress terrain scan also wanting to move
the mast platform. That's intentionally deferred until command_node grows
real mode arbitration -- until then, don't run LED tracking and a terrain
scan at the same time.
"""

import itertools
from collections import Counter

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration

from geometry_msgs.msg import PoseStamped, TransformStamped

import tf2_ros
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares

from rover_perception_msgs.msg import LedDetectionArray
from rover_control_msgs.msg import OperationalModeSettings, MotorPosition


DEFAULTS = {
    "detections_topic": "/mono_cam/led_detections",
    "pose_topic": "/rover/estimated_pose",
    "world_frame": "world",
    "state_topic": "/operational_mode/settings",
    # TF child frame this node broadcasts for the solved rover pose, purely
    # for RViz2 visualization -- not consumed by any other node (yet).
    "rover_frame": "rover_estimated_link",

    # ------------------------------------------------------------------
    # The single LED pattern's geometry, in its own local frame (x=right
    # as drawn, y=up as drawn, z=0 -- flat). Measured 2026-09 -- see module
    # docstring for the physical layout and how it was confirmed.
    # ------------------------------------------------------------------
    "led1_x_m": 0.0000, "led1_y_m": 0.0000, "led1_color": "blue",
    "led2_x_m": 0.0326, "led2_y_m": 0.0000, "led2_color": "blue",
    "led3_x_m": 0.0503, "led3_y_m": 0.0249, "led3_color": "red",
    "led4_x_m": 0.0665, "led4_y_m": 0.0000, "led4_color": "blue",

    # ------------------------------------------------------------------
    # Pattern mounting, relative to rover center, in THIS FILE's rover-
    # local axes (x=forward, y=left, z=up -- see module docstring). Pattern
    # faces forward; mount_offset is LED1's (the pattern's local origin)
    # position relative to rover center.
    # ------------------------------------------------------------------
    "mount_forward_m": 0.010,
    "mount_left_m": 0.035,
    "mount_up_m": 0.024,

    # Exact color counts are derived from led1..4_color above, but the
    # pattern needs to see ALL of its LEDs to attempt a solve -- no partial
    # fits from a partially occluded view.
    "min_detections": 4,

    # If the best fit's RMS bearing residual (converted to an approximate
    # angle) exceeds this, the frame is dropped as unreliable rather than
    # publishing a bad pose.
    "max_fit_residual_deg": 3.0,

    "tf_timeout_sec": 0.3,

    # ------------------------------------------------------------------
    # Active pan/tilt search + centering -- see module docstring.
    # ------------------------------------------------------------------
    "motor_position_topic": "/motor_position/current",
    "motor_position_cmd_topic": "/motor_position/new",

    "pan_motor_field": "motor5",
    "tilt_motor_field": "motor1",

    # Pan motor: Dynamixel AX-12A (see datasheet). Joint Mode only reaches
    # raw 0..1023 = 0..300 deg -- 300-360 deg is mechanically invalid, that
    # ~60 deg gap is the "dead zone" referenced throughout this file.
    "pan_raw_min": 0,
    "pan_raw_max": 1023,
    "pan_raw_center": 512,
    "pan_deg_per_raw": 0.29,

    # Tilt motor: a DIFFERENT model than the pan motor -- numbers from its
    # own datasheet. Using its "Recommended Range" (21..1002) rather than
    # the absolute full range (0..1023) as the usable bound here, since
    # running right at the mechanical hard stops during normal operation
    # isn't advisable. Adjust if you'd rather use the full range.
    "tilt_raw_min": 21,
    "tilt_raw_max": 1002,
    "tilt_raw_center": 512,
    "tilt_deg_per_raw": 0.325,

    # Pan/tilt position (raw) held during the search sweep and while a
    # correction is blocked. Tilt never sweeps on its own (only pan does).
    "tilt_home_raw": 512,

    # Search sweep.
    "search_step_deg": 20.0,
    # Consecutive valid-fit frames required to declare "found" at a search
    # position -- more than 1 so a single noisy frame can't stop the sweep.
    "search_confirm_frames": 3,
    # Give up on a search position (move to the next) after this many
    # camera frames without confirming, once arrived.
    "search_dwell_frames": 20,
    "search_arrival_tolerance_raw": 5,
    # If /motor_position/current never confirms arrival within this many
    # frames (feedback lag/dropout), proceed anyway rather than stalling
    # the whole search forever.
    "search_arrival_timeout_frames": 60,

    # Tracking / deadband -- independent per axis.
    "pan_deadband_deg": 5.0,
    "tilt_deadband_deg": 5.0,
    # Consecutive frames with no valid fit before the pattern counts as
    # "lost" during tracking. Deliberately generous per request.
    "lost_confirm_frames": 15,

    # Physical correction direction hasn't been confirmed on real hardware
    # yet -- flip to -1 for either axis if a live test overcorrects the
    # wrong way (see module docstring).
    "pan_correction_sign": 1,
    "tilt_correction_sign": 1,
}

# Yaw seeds (degrees, rotation about the camera/world "up"-ish Y axis) tried
# per correspondence candidate, purely to help the nonlinear solver avoid a
# bad local minimum for large rotations -- see module docstring point 3.
_SEED_YAW_DEG = (0.0, 90.0, 180.0, 270.0)


def _build_led_local_points(defaults: dict) -> tuple:
    """The single LED pattern's shape, as 3D points in its own local frame
    (x=right as drawn, y=up as drawn, z=0 -- flat), plus a parallel list of
    each point's color. Order matches LED1..LED4 as measured -- see module
    docstring.
    """
    points = np.array([
        [defaults["led1_x_m"], defaults["led1_y_m"], 0.0],
        [defaults["led2_x_m"], defaults["led2_y_m"], 0.0],
        [defaults["led3_x_m"], defaults["led3_y_m"], 0.0],
        [defaults["led4_x_m"], defaults["led4_y_m"], 0.0],
    ], dtype=np.float64)
    colors = [
        defaults["led1_color"], defaults["led2_color"],
        defaults["led3_color"], defaults["led4_color"],
    ]
    return points, colors


def _mount_rotation(right_axis: np.ndarray, up_axis: np.ndarray, normal: np.ndarray) -> np.ndarray:
    """Pattern-local -> rover-local rotation matrix, built from the
    pattern's own basis vectors (as columns). right_axis/up_axis/normal
    must form a proper (determinant +1) orthonormal basis, i.e.
    normal = right x up -- see module docstring for how these were derived
    for this pattern's actual mounting.
    """
    return np.column_stack([right_axis, up_axis, normal])


class PositionRoverNode(Node):

    def __init__(self):
        super().__init__("position_rover_node")

        self._declare_parameters()
        self._load_parameters()
        self.state = "OFF"  # default

        self.sub = None
        self.pose_pub = None

        self.motor_position_sub = None
        self.motor_cmd_pub = None
        self._latest_motor_position = None
        self._reset_pan_tilt_state()

        self.state_sub = self.create_subscription(
            OperationalModeSettings,
            self.state_topic,
            self.state_callback,
            10,
        )

    def state_callback(self, msg):
        if self.state == msg.mono_cam:
            return

        self.state = msg.mono_cam

        if self.state == "OFF":
            self.get_logger().info(f"position_rover_node: OFF")

            self.destroy_subscription(self.sub)
            self.destroy_publisher(self.pose_pub)
            self.destroy_subscription(self.motor_position_sub)
            self.destroy_publisher(self.motor_cmd_pub)

            self.sub = None
            self.pose_pub = None
            self.motor_position_sub = None
            self.motor_cmd_pub = None
            self._latest_motor_position = None
            self._reset_pan_tilt_state()

            # 1. Listener und Broadcaster deaktivieren (auf None setzen)
            self.tf_listener.unregister()
            self.tf_broadcaster.destroy()

            self.tf_listener = None
            self.tf_buffer = None
            self.tf_broadcaster = None

        elif self.state == "ON":
            self.get_logger().info(f"position_rover_node: ON")

            current_params = {name: getattr(self, name) for name in DEFAULTS}
            self._local_points, self._local_colors = _build_led_local_points(current_params)

            # Which local point indices belong to each color, and how many
            # of each color the pattern needs to see -- derived from the
            # measured geometry, not hardcoded, so a future pattern with a
            # different color layout doesn't need this logic touched. See
            # module docstring "Color-constrained correspondence search".
            self._color_local_indices: dict = {}
            for idx, color in enumerate(self._local_colors):
                self._color_local_indices.setdefault(color, []).append(idx)
            self._required_color_counts = dict(Counter(self._local_colors))

            # Precomputed once: every within-color permutation of detection
            # order -> local-point order, for each color that has more than
            # one point (a single-point color has only the trivial
            # permutation). Combined per-frame via itertools.product to
            # build the full set of candidate correspondences.
            self._color_perms = {
                color: list(itertools.permutations(range(len(indices))))
                for color, indices in self._color_local_indices.items()
            }

            # Single mounting extrinsics (pattern-local -> rover-local) --
            # see module docstring for how right_axis/up_axis/normal and
            # mount_offset were derived for this pattern's actual mounting.
            self._R_mount = _mount_rotation(
                right_axis=np.array([0.0, 1.0, 0.0]),   # pattern local +x -> rover left
                up_axis=np.array([0.0, 0.0, 1.0]),       # pattern local +y -> rover up
                normal=np.array([1.0, 0.0, 0.0]),        # pattern local +z -> rover forward
            )
            self._mount_offset = np.array([
                self.mount_forward_m, self.mount_left_m, self.mount_up_m,
            ])

            self._seed_rotvecs = [
                Rotation.from_euler("y", deg, degrees=True).as_rotvec()
                for deg in _SEED_YAW_DEG
            ]

            self.sub = self.create_subscription(
                LedDetectionArray,
                self.detections_topic,
                self.detections_callback,
                10,
            )

            self.pose_pub = self.create_publisher(
                PoseStamped,
                self.pose_topic,
                10,
            )

            self.motor_position_sub = self.create_subscription(
                MotorPosition,
                self.motor_position_topic,
                self._motor_position_callback,
                10,
            )

            self.motor_cmd_pub = self.create_publisher(
                MotorPosition,
                self.motor_position_cmd_topic,
                10,
            )

            self._reset_pan_tilt_state()

            self.tf_buffer = tf2_ros.Buffer()
            self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
            self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

            self.get_logger().info(
                f"position_rover_node: {self.detections_topic} -> "
                f"{self.pose_topic} (world_frame={self.world_frame}, "
                f"single LED pattern, colors={self._local_colors}, "
                f"required_counts={self._required_color_counts}); "
                f"pan/tilt search+tracking via {self.motor_position_topic} -> "
                f"{self.motor_position_cmd_topic}"
            )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    # ------------------------------------------------------------------
    # Main callback
    # ------------------------------------------------------------------
    def detections_callback(self, msg: LedDetectionArray):
        try:
            n = len(msg.detections)
            if n < self.min_detections:
                self.get_logger().debug(
                    f"Only {n} LED detections, need >= "
                    f"{self.min_detections}. Skipping frame."
                )
                self._update_pan_tilt_control(found_this_frame=False, mean_bearing=None)
                return

            groups: dict = {}
            for d in msg.detections:
                color = self._classify_color(d.color_r, d.color_g, d.color_b)
                if color not in self._color_local_indices:
                    continue  # e.g. a stray green-dominant blob -- noise
                groups.setdefault(color, []).append(d)

            if any(
                len(groups.get(color, [])) != count
                for color, count in self._required_color_counts.items()
            ):
                self.get_logger().warn(
                    "Detected LEDs don't match the expected pattern this "
                    f"frame (need {self._required_color_counts}, got "
                    f"{ {c: len(v) for c, v in groups.items()} }). "
                    "Skipping frame.",
                    throttle_duration_sec=5.0,
                )
                self._update_pan_tilt_control(found_this_frame=False, mean_bearing=None)
                return

            all_bearings = []
            for dets in groups.values():
                for d in dets:
                    all_bearings.append((d.bearing.x, d.bearing.y, d.bearing.z))
            all_bearings = np.array(all_bearings, dtype=np.float64)
            all_bearings = all_bearings / np.linalg.norm(all_bearings, axis=1, keepdims=True)
            mean_bearing = all_bearings.mean(axis=0)

            candidates = self._build_color_constrained_correspondences(groups)

            t_seed = self._initial_translation_guess(all_bearings, self._local_points)
            result = self._search_best_pose(candidates, self._local_points, t_seed)

            if result is None:
                self.get_logger().warn(
                    "No correspondence produced a valid fit this frame.",
                    throttle_duration_sec=5.0,
                )
                self._update_pan_tilt_control(found_this_frame=False, mean_bearing=None)
                return

            rms_deg, rotmat_cam_pattern, t_cam_pattern = result
            if rms_deg > self.max_fit_residual_deg:
                self.get_logger().warn(
                    f"Best fit residual {rms_deg:.2f} deg exceeds "
                    f"max_fit_residual_deg={self.max_fit_residual_deg}. "
                    "Skipping frame.",
                    throttle_duration_sec=5.0,
                )
                self._update_pan_tilt_control(found_this_frame=False, mean_bearing=None)
                return

            rotmat_cam_rover, t_cam_rover = self._compose_rover_pose(
                rotmat_cam_pattern, t_cam_pattern,
            )

            self._publish_world_pose(msg, rotmat_cam_rover, t_cam_rover)
            self._update_pan_tilt_control(found_this_frame=True, mean_bearing=mean_bearing)

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"detections_callback failed: {exc}")

    # ------------------------------------------------------------------
    # Color classification
    # ------------------------------------------------------------------
    def _classify_color(self, r: float, g: float, b: float) -> str:
        """Which color a detection is, by its dominant channel. Only "red"
        and "blue" mean anything for this pattern -- a "green" result is
        noise (a reflection, another light source) and gets dropped by the
        caller, since this pattern has no green LED.
        """
        idx = int(np.argmax([r, g, b]))
        return ("red", "green", "blue")[idx]

    # ------------------------------------------------------------------
    # Color-constrained correspondence search -- see module docstring.
    # ------------------------------------------------------------------
    def _build_color_constrained_correspondences(self, groups: dict) -> list:
        """Builds every valid (bearing detection -> local point) ordering,
        constrained by color: only permutes detections within the same
        color group, then takes the Cartesian product across colors. For
        this pattern (3 blue + 1 red) that's 3! x 1! = 6 candidates, not
        the old unconstrained 4! = 24.
        """
        colors = list(self._color_local_indices.keys())
        per_color_choices = [self._color_perms[color] for color in colors]

        candidates = []
        for choice in itertools.product(*per_color_choices):
            ordered = [None] * len(self._local_points)
            for color, perm in zip(colors, choice):
                local_indices = self._color_local_indices[color]
                dets = groups[color]
                for local_idx, det_idx in zip(local_indices, perm):
                    d = dets[det_idx]
                    ordered[local_idx] = (d.bearing.x, d.bearing.y, d.bearing.z)
            candidates.append(np.array(ordered, dtype=np.float64))

        return candidates

    # ------------------------------------------------------------------
    # Pose search
    # ------------------------------------------------------------------
    def _initial_translation_guess(self, bearings: np.ndarray, local_points: np.ndarray) -> np.ndarray:
        """Rough initial distance estimate from the pattern's known size and
        its apparent angular spread (small-angle approximation -- refined
        immediately afterward by least_squares, this only needs to be in
        the right ballpark to help the optimizer converge).
        """
        mean_dir = bearings.mean(axis=0)
        mean_dir = mean_dir / np.linalg.norm(mean_dir)

        cos_pairwise = np.clip(bearings @ bearings.T, -1.0, 1.0)
        max_angle = float(np.arccos(cos_pairwise).max())
        max_angle = max(max_angle, 1e-4)

        pairwise_dists = np.linalg.norm(
            local_points[:, None, :] - local_points[None, :, :], axis=2
        )
        pattern_extent_m = float(pairwise_dists.max())
        distance_guess = float(np.clip(pattern_extent_m / max_angle, 0.3, 20.0))

        return mean_dir * distance_guess

    def _solve_pose(self, obs_bearings, local_points, rotvec_seed, t_seed):
        def residuals(params):
            rotvec = params[:3]
            t = params[3:6]
            rot = Rotation.from_rotvec(rotvec).as_matrix()
            predicted = (rot @ local_points.T).T + t
            norms = np.clip(
                np.linalg.norm(predicted, axis=1, keepdims=True), 1e-6, None
            )
            predicted_dir = predicted / norms
            return (predicted_dir - obs_bearings).ravel()

        x0 = np.concatenate([rotvec_seed, t_seed])
        try:
            return least_squares(residuals, x0, method="lm", max_nfev=200)
        except Exception:  # noqa: BLE001
            return None

    def _search_best_pose(self, candidates: list, local_points, t_seed):
        """Tries every (candidate correspondence x yaw seed) combination,
        returns (rms_residual_deg, rotation_matrix, translation)
        [camera <- pattern] for whichever converged to the lowest cost, or
        None if nothing did.
        """
        best_cost = None
        best_result = None

        for candidate in candidates:
            for rotvec_seed in self._seed_rotvecs:
                result = self._solve_pose(candidate, local_points, rotvec_seed, t_seed)
                if result is None or not result.success:
                    continue
                if best_cost is None or result.cost < best_cost:
                    best_cost = result.cost
                    best_result = result

        if best_result is None:
            return None

        rms_residual_rad = float(np.sqrt(np.mean(best_result.fun ** 2)))
        rms_residual_deg = np.degrees(rms_residual_rad)

        rotvec = best_result.x[:3]
        t = best_result.x[3:6]
        rotmat = Rotation.from_rotvec(rotvec).as_matrix()

        return rms_residual_deg, rotmat, t

    # ------------------------------------------------------------------
    # Pattern pose -> rover-center pose
    # ------------------------------------------------------------------
    def _compose_rover_pose(self, rotmat_cam_pattern, t_cam_pattern):
        """Given a solved camera<-pattern pose and the pattern's fixed
        mounting extrinsics (rover-local rotation + offset), returns the
        camera<-rover pose.

        Derivation: a point on the pattern satisfies both
            X_camera  = rotmat_cam_pattern @ X_pattern + t_cam_pattern
            X_pattern = R_mount.T @ (X_rover - mount_offset)
        (the second line just inverts "X_rover = mount_offset +
        R_mount @ X_pattern", the pattern's placement relative to the rover
        center). Substituting gives X_camera = R_cr @ X_rover + t_cr with:
            R_cr = rotmat_cam_pattern @ R_mount.T
            t_cr = t_cam_pattern - rotmat_cam_pattern @ R_mount.T @ mount_offset
        which is exactly the rover center's pose in the camera frame (at
        X_rover = 0, X_camera = t_cr).
        """
        rotmat_cam_rover = rotmat_cam_pattern @ self._R_mount.T
        t_cam_rover = t_cam_pattern - rotmat_cam_pattern @ self._R_mount.T @ self._mount_offset

        return rotmat_cam_rover, t_cam_rover

    # ------------------------------------------------------------------
    # World-frame composition + publishing
    # ------------------------------------------------------------------
    def _publish_world_pose(self, msg: LedDetectionArray, rotmat_cam_rover, t_cam_rover):
        camera_frame = msg.header.frame_id

        try:
            transform = self.tf_buffer.lookup_transform(
                self.world_frame,
                camera_frame,
                msg.header.stamp,
                timeout=Duration(seconds=self.tf_timeout_sec),
            )
        except (
            tf2_ros.LookupException,
            tf2_ros.ConnectivityException,
            tf2_ros.ExtrapolationException,
        ) as exc:
            self.get_logger().warn(
                f"No transform {camera_frame} -> {self.world_frame} yet: "
                f"{exc}. Dropping this pose estimate.",
                throttle_duration_sec=5.0,
            )
            return

        q = transform.transform.rotation
        world_R_camera = Rotation.from_quat([q.x, q.y, q.z, q.w]).as_matrix()
        world_t_camera = np.array([
            transform.transform.translation.x,
            transform.transform.translation.y,
            transform.transform.translation.z,
        ])

        world_R_rover = world_R_camera @ rotmat_cam_rover
        world_t_rover = world_R_camera @ t_cam_rover + world_t_camera

        world_quat = Rotation.from_matrix(world_R_rover).as_quat()  # x,y,z,w

        pose_msg = PoseStamped()
        pose_msg.header.stamp = msg.header.stamp
        pose_msg.header.frame_id = self.world_frame
        pose_msg.pose.position.x = float(world_t_rover[0])
        pose_msg.pose.position.y = float(world_t_rover[1])
        pose_msg.pose.position.z = float(world_t_rover[2])
        pose_msg.pose.orientation.x = float(world_quat[0])
        pose_msg.pose.orientation.y = float(world_quat[1])
        pose_msg.pose.orientation.z = float(world_quat[2])
        pose_msg.pose.orientation.w = float(world_quat[3])
        self.pose_pub.publish(pose_msg)

        tf_msg = TransformStamped()
        tf_msg.header.stamp = msg.header.stamp
        tf_msg.header.frame_id = self.world_frame
        tf_msg.child_frame_id = self.rover_frame
        tf_msg.transform.translation.x = float(world_t_rover[0])
        tf_msg.transform.translation.y = float(world_t_rover[1])
        tf_msg.transform.translation.z = float(world_t_rover[2])
        tf_msg.transform.rotation.x = float(world_quat[0])
        tf_msg.transform.rotation.y = float(world_quat[1])
        tf_msg.transform.rotation.z = float(world_quat[2])
        tf_msg.transform.rotation.w = float(world_quat[3])
        self.tf_broadcaster.sendTransform(tf_msg)

    # ------------------------------------------------------------------
    # Pan/tilt search + centering -- see module docstring.
    # ------------------------------------------------------------------
    def _reset_pan_tilt_state(self):
        self._tracking = False
        self._search_started = False
        self._search_exhausted = False
        self._search_positions = []
        self._search_index = 0
        self._search_phase = "moving"
        self._arrival_wait_frames = 0
        self._dwell_frame_count = 0
        self._valid_streak = 0
        self._invalid_streak = 0
        self._pan_blocked = False
        self._tilt_blocked = False
        self._pan_blocked_at_min = False
        self._pan_blocked_at_max = False

    def _motor_position_callback(self, msg: MotorPosition):
        self._latest_motor_position = msg

    def _pan_raw_to_deg(self, raw):
        return (raw - self.pan_raw_center) * self.pan_deg_per_raw

    def _pan_deg_to_raw(self, deg):
        return self.pan_raw_center + deg / self.pan_deg_per_raw

    def _tilt_raw_to_deg(self, raw):
        return (raw - self.tilt_raw_center) * self.tilt_deg_per_raw

    def _tilt_deg_to_raw(self, deg):
        return self.tilt_raw_center + deg / self.tilt_deg_per_raw

    def _send_motor_command(self, pan_raw=None, tilt_raw=None):
        """Publishes a full MotorPosition command, echoing back the other
        3 motors' last known real values -- see module docstring, this is
        an absolute 5-motor setpoint, not a per-motor delta."""

        if self._latest_motor_position is None:
            self.get_logger().warn(
                f"Cannot send a motor command yet -- no {self.motor_position_topic} "
                "feedback received, don't know the other motors' current values.",
                throttle_duration_sec=5.0,
            )
            return

        cmd = MotorPosition()
        cmd.motor1 = self._latest_motor_position.motor1
        cmd.motor2 = self._latest_motor_position.motor2
        cmd.motor3 = self._latest_motor_position.motor3
        cmd.motor4 = self._latest_motor_position.motor4
        cmd.motor5 = self._latest_motor_position.motor5

        if pan_raw is not None:
            setattr(cmd, self.pan_motor_field,
                    int(np.clip(pan_raw, self.pan_raw_min, self.pan_raw_max)))
        if tilt_raw is not None:
            setattr(cmd, self.tilt_motor_field,
                    int(np.clip(tilt_raw, self.tilt_raw_min, self.tilt_raw_max)))

        self.motor_cmd_pub.publish(cmd)

    def _build_search_positions(self, start_at: str):
        """Pan raw positions to sweep, search_step_deg apart, covering the
        full reachable range, starting from one edge. Always includes the
        far endpoint exactly even if the step doesn't divide evenly."""

        step_raw = max(1, int(round(self.search_step_deg / self.pan_deg_per_raw)))

        if start_at == "min":
            positions = list(range(self.pan_raw_min, self.pan_raw_max, step_raw))
            positions.append(self.pan_raw_max)
        else:
            positions = list(range(self.pan_raw_max, self.pan_raw_min, -step_raw))
            positions.append(self.pan_raw_min)

        return positions

    def _start_search(self, start_at: str = "min"):
        self._tracking = False
        self._pan_blocked = False
        self._tilt_blocked = False
        self._search_exhausted = False
        self._search_positions = self._build_search_positions(start_at)
        self._search_index = 0
        self._advance_to_next_search_position()

    def _advance_to_next_search_position(self):
        if self._search_index >= len(self._search_positions):
            self.get_logger().error(
                "LED-Suchlauf abgeschlossen -- kein Pattern ueber den "
                "gesamten erreichbaren Pan-Bereich gefunden."
            )
            self._search_exhausted = True
            return

        target_raw = self._search_positions[self._search_index]
        self._search_phase = "moving"
        self._arrival_wait_frames = 0
        self._send_motor_command(pan_raw=target_raw, tilt_raw=self.tilt_home_raw)
        self.get_logger().info(
            f"LED-Suchlauf: naechste Pan-Position raw={target_raw} "
            f"({self._pan_raw_to_deg(target_raw):.1f} deg)"
        )

    def _update_search(self, found_this_frame):
        current_pan_raw = getattr(self._latest_motor_position, self.pan_motor_field)

        if not self._search_exhausted and self._search_phase == "moving":
            target_raw = self._search_positions[self._search_index]
            self._arrival_wait_frames += 1
            arrived = abs(current_pan_raw - target_raw) <= self.search_arrival_tolerance_raw
            timed_out = self._arrival_wait_frames >= self.search_arrival_timeout_frames
            if not (arrived or timed_out):
                return  # still slewing -- don't evaluate detections yet
            self._search_phase = "watching"
            self._dwell_frame_count = 0
            self._valid_streak = 0

        if found_this_frame:
            self._valid_streak += 1
        else:
            self._valid_streak = 0

        if self._valid_streak >= self.search_confirm_frames:
            self.get_logger().info("LED-Pattern gefunden -- wechsle zu Tracking.")
            self._tracking = True
            self._invalid_streak = 0
            return

        if self._search_exhausted:
            return  # parked, but still listening above for a lucky find

        self._dwell_frame_count += 1
        if self._dwell_frame_count >= self.search_dwell_frames:
            self._search_index += 1
            self._advance_to_next_search_position()

    def _update_tracking(self, found_this_frame, mean_bearing):
        if not found_this_frame:
            self._invalid_streak += 1
            if self._invalid_streak >= self.lost_confirm_frames:
                self.get_logger().warn("LED-Pattern verloren -- starte Suchlauf neu.")
                # Resume at the opposite edge from wherever pan was blocked
                # right before losing it -- see module docstring. Tilt has
                # no search of its own, so only pan's block matters here.
                if self._pan_blocked_at_min:
                    start_at = "max"
                elif self._pan_blocked_at_max:
                    start_at = "min"
                else:
                    start_at = "min"
                self._start_search(start_at)
            return

        self._invalid_streak = 0

        # Deviation from "dead ahead" straight from the bearing vector --
        # no separate CameraInfo needed, bearing already encodes it.
        pan_dev_deg = float(np.degrees(np.arctan2(mean_bearing[0], mean_bearing[2])))
        tilt_dev_deg = float(np.degrees(np.arctan2(mean_bearing[1], mean_bearing[2])))

        current_pan_raw = getattr(self._latest_motor_position, self.pan_motor_field)
        current_tilt_raw = getattr(self._latest_motor_position, self.tilt_motor_field)

        new_pan_raw = None
        new_tilt_raw = None

        if abs(pan_dev_deg) > self.pan_deadband_deg:
            target_pan_deg = self._pan_raw_to_deg(current_pan_raw) + self.pan_correction_sign * pan_dev_deg
            target_pan_raw = int(round(self._pan_deg_to_raw(target_pan_deg)))

            if self.pan_raw_min <= target_pan_raw <= self.pan_raw_max:
                new_pan_raw = target_pan_raw
                self._pan_blocked = False
                self._pan_blocked_at_min = False
                self._pan_blocked_at_max = False
            else:
                # Would need to move into the dead zone -- hold instead of
                # correcting (see module docstring), remember which edge.
                self._pan_blocked = True
                self._pan_blocked_at_min = target_pan_raw < self.pan_raw_min
                self._pan_blocked_at_max = target_pan_raw > self.pan_raw_max
                self.get_logger().warn(
                    f"Pan-Korrektur wuerde in den toten Winkel fuehren (Ziel-raw "
                    f"{target_pan_raw}, Bereich [{self.pan_raw_min}, {self.pan_raw_max}]) "
                    "-- halte Position, folge nicht weiter.",
                    throttle_duration_sec=2.0,
                )
        else:
            self._pan_blocked = False
            self._pan_blocked_at_min = False
            self._pan_blocked_at_max = False

        if abs(tilt_dev_deg) > self.tilt_deadband_deg:
            target_tilt_deg = self._tilt_raw_to_deg(current_tilt_raw) + self.tilt_correction_sign * tilt_dev_deg
            target_tilt_raw = int(round(self._tilt_deg_to_raw(target_tilt_deg)))

            if self.tilt_raw_min <= target_tilt_raw <= self.tilt_raw_max:
                new_tilt_raw = target_tilt_raw
                self._tilt_blocked = False
            else:
                self._tilt_blocked = True
                self.get_logger().warn(
                    f"Tilt-Korrektur wuerde ausserhalb des erreichbaren Bereichs liegen "
                    f"(Ziel-raw {target_tilt_raw}, Bereich [{self.tilt_raw_min}, "
                    f"{self.tilt_raw_max}]) -- halte Position, folge nicht weiter.",
                    throttle_duration_sec=2.0,
                )
        else:
            self._tilt_blocked = False

        if new_pan_raw is not None or new_tilt_raw is not None:
            self._send_motor_command(pan_raw=new_pan_raw, tilt_raw=new_tilt_raw)

    def _update_pan_tilt_control(self, found_this_frame, mean_bearing):
        if self._latest_motor_position is None:
            return  # no feedback yet -- don't command anything blind

        if not self._search_started:
            self._search_started = True
            self._start_search(start_at="min")

        if self._tracking:
            self._update_tracking(found_this_frame, mean_bearing)
        else:
            self._update_search(found_this_frame)


def main(args=None):
    rclpy.init(args=args)

    node = PositionRoverNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()