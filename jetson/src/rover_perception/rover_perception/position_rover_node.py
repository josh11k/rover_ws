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

This is written generically (group detections by color, require *at least*
the count of each color the model has, choose-and-order that many out of
however many showed up, per color, then take the Cartesian product across
colors) rather than hardcoded to "3 blue + 1 red", so a future pattern with
a different color layout doesn't need this logic rewritten, just the LED_*
DEFAULTS below changed.

Tolerating extra detections per color (added 2026-09, for reflections)
-----------------------------------------------------------------------------
Real-world testing showed LED reflections (off nearby shiny surfaces) can
show up as additional same-colored detections led_detector_node has no way
to distinguish from the real thing on its own. Rather than requiring an
*exact* color count (which meant a single stray reflection dropped the
whole frame), this now requires only *at least* the model's count per
color, and searches every way to choose-and-order that many detections out
of however many arrived. Concretely: `itertools.permutations(dets, r)`
already does exactly "choose r out of len(dets), in every order" in one
call -- no separate combinations-then-permutations step needed.

This leans on the same residual-based rejection already in place
(max_fit_residual_deg): the pattern's asymmetric, exactly-known geometry
means a reflection standing in for a real LED essentially never fits the
rigid 4-point shape as well as the true correspondence does, so it should
lose out to the correct one on residual alone.

Two trade-offs that come with this, deliberately not addressed further
right now (see chat -- this change is scoped to "tolerate a few extra
detections", not a general noise-robustness overhaul):

  - Combinatorics grow fast with extra detections: choosing-and-ordering 3
    out of 7 blue detections (3 real + 4 reflections) is P(7,3) = 210
    candidates instead of 6, x4 yaw seeds = 840 solves instead of 24 for
    that color alone. max_candidates_per_color below is a blunt safety
    valve (keeps only the largest-area detections per color beyond that
    count) so a noisy frame can't make this unboundedly expensive -- raise
    it only if you've confirmed the Jetson keeps up.
  - More candidates statistically raises (slightly) the chance some wrong
    combination fits deceptively well purely by chance, since
    max_fit_residual_deg is an absolute threshold, not a "clearly better
    than the next-best candidate" margin check. Not addressed here --
    revisit if real testing shows false-positive poses.

Separately, two known weaknesses in the underlying pose fit itself (very
oblique viewing angles causing foreshortening/dimming; the classical
monocular planar-pose ambiguity at near-frontal, distant views) were
discussed in chat and are explicitly NOT addressed by this change -- see
chat for the details if those need tackling later.

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

Active pan/tilt search + centering (added 2026-09; motor wiring rewritten
2026-09 -- pan and tilt now use two completely separate motors/topics, see
below)
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
  range (pan_min_deg..pan_max_deg) in search_step_deg increments, tilt held
  fixed at tilt_home_raw. At each step: wait (via /xm430_node/new_position
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
  that axis (pan via /xm430_node/goal_position, tilt via
  /motor_position/goal_position). If lost_confirm_frames *consecutive*
  frames report no valid fit, the pattern is considered lost and a new
  search starts.

Two physically different motors, two completely separate topic pairs
(2026-09 -- pan and tilt motor MODELS were swapped relative to the earlier
design; see chat)
-----------------------------------------------------------------------------
Tilt (and the drive motors) -- Dynamixel AX-12A, via the shared
MotorPosition message (rover_control_msgs/msg/MotorPosition), reduced from
5 to 4 fields (motor1=tilt, motor2-4=drive/other; motor5/pan removed --
see below). Topics renamed too:
    /motor_position/new_position   (sub, feedback)
    /motor_position/goal_position  (pub, command)
This is still an *absolute* 4-motor command, not a per-motor delta (see
stm_bridge_node_V2.py). Every command this node sends echoes back the
other 2 drive motors' last known real values from /motor_position/
new_position untouched, so a tilt correction never accidentally stomps on
whatever the drive motors were doing. AX-12A Joint Mode only reaches raw
0..1023 = 0..300 deg -- 300-360 deg is mechanically invalid, a ~60 deg gap
it can never reach (the "dead zone" referenced below, now specifically a
TILT concern -- this used to be pan's constraint before the motor swap).

Pan -- Dynamixel XM430-W350, via its own dedicated xm430_node (package
dxl_xm430_control), NOT bundled into MotorPosition at all:
    /xm430_node/new_position   (sub, feedback) -- std_msgs/Float64, RADIANS
    /xm430_node/goal_position  (pub, command)  -- std_msgs/Float64, RADIANS
(0 rad = xm430_node's own center convention, tick 2048 of 4096). Since
xm430_node works in a single float per message (no other motors sharing
this topic), no echo-back is needed for pan the way tilt needs one for its
drive motors. Converted to/from degrees in this file only for consistency
with the rest of its parameters (deadband, search step), which are all in
degrees -- np.radians/np.degrees at the message boundary, nowhere else.

Confirmed reachable pan range: 0-360 deg (effectively the full circle --
the XM430-W350's Position Control Mode covers 0..4095 ticks internally,
~360 deg, unlike the AX-12A's 300 deg limit it replaced for this axis).
NOT confirmed: whether commanding across the 0/360 deg seam (e.g. 350 deg
-> 10 deg) makes the servo take the short way around or the long way --
Dynamixel Position Control Mode (as opposed to Extended Position Control
Mode, which this node is NOT configured for -- see xm430_node.py) does not
necessarily wrap ticks automatically the way a truly continuous joint
would. Until this is verified on real hardware, pan_min_deg/pan_max_deg
below are treated as a soft boundary -- hold instead of crossing it --
using the exact same block-and-resume-at-opposite-edge mechanism the old
AX-12A dead zone used, even though this is a precaution against an
unconfirmed wraparound behavior rather than a truly unreachable mechanical
gap like the old dead zone was. Revisit (and potentially just wrap
normally) once tested for real.

Tilt has no search of its own (only pan sweeps; tilt is assumed roughly
constant height), so only pan's block direction matters for where the next
search resumes.

pan_correction_sign/tilt_correction_sign exist because the real physical
direction (does increasing raw/rad actually move toward where the pattern
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
from std_msgs.msg import Float64

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

    # Minimum color counts are derived from led1..4_color above, but the
    # pattern needs to see ALL of its LEDs to attempt a solve -- no partial
    # fits from a partially occluded view. This is a floor, not an exact
    # requirement -- see "Tolerating extra detections per color" above.
    "min_detections": 4,

    # Safety valve against combinatorial blowup when extra same-colored
    # detections (reflections) show up -- see "Tolerating extra detections
    # per color" above. If more than this many detections of one color
    # arrive in a frame, only the largest-area ones (by led_detector_node's
    # area_px) are kept before the correspondence search runs. Real LEDs
    # seen directly are generally larger/brighter than their reflections,
    # though this is a heuristic, not a guarantee.
    "max_candidates_per_color": 8,

    # If the best fit's RMS bearing residual (converted to an approximate
    # angle) exceeds this, the frame is dropped as unreliable rather than
    # publishing a bad pose.
    "max_fit_residual_deg": 3.0,

    "tf_timeout_sec": 0.3,

    # ------------------------------------------------------------------
    # Active pan/tilt search + centering -- see module docstring "Two
    # physically different motors, two completely separate topic pairs".
    # ------------------------------------------------------------------

    # Tilt + drive motors -- Dynamixel AX-12A, via the shared MotorPosition
    # message. Renamed/reduced 2026-09: this message now has 4 fields
    # (motor1=tilt, motor2-4=drive), motor5 (pan) was removed since pan
    # moved to its own dedicated topics below (a different physical motor,
    # XM430-W350, controlled by its own node).
    "tilt_motor_topic": "/motor_position/new_position",
    "tilt_motor_cmd_topic": "/motor_position/goal_position",
    "tilt_motor_field": "motor1",

    # AX-12A (see datasheet): Joint Mode raw 0..1023 = 0..300 deg -- 300-360
    # deg is mechanically invalid, that ~60 deg gap is the "dead zone"
    # referenced throughout this file, now specifically a TILT concern
    # (pan and tilt motor models were swapped 2026-09 -- see chat).
    "tilt_raw_min": 0,
    "tilt_raw_max": 1023,
    "tilt_raw_center": 512,
    "tilt_deg_per_raw": 0.29,

    # Tilt position (raw) held during the search sweep and while a pan
    # correction is blocked. Tilt never sweeps on its own (only pan does).
    "tilt_home_raw": 512,

    # Pan -- Dynamixel XM430-W350, via its own dedicated xm430_node, NOT
    # bundled into MotorPosition. Wire format is std_msgs/Float64 in
    # RADIANS (0 rad = xm430_node's own center convention) -- converted
    # to/from degrees here only for consistency with the rest of this
    # file's deadband/search-step parameters, which are all in degrees.
    "pan_topic": "/xm430_node/new_position",
    "pan_cmd_topic": "/xm430_node/goal_position",

    # Confirmed reachable range: 0-360 deg (effectively the full circle).
    # Treated as a soft boundary (hold, don't cross) rather than assumed-
    # safe wraparound -- see module docstring for why this is unconfirmed
    # rather than a known mechanical limit like the old AX-12A dead zone.
    "pan_min_deg": 0.0,
    "pan_max_deg": 360.0,
    "pan_home_deg": 180.0,

    # Search sweep.
    "search_step_deg": 20.0,
    # Consecutive valid-fit frames required to declare "found" at a search
    # position -- more than 1 so a single noisy frame can't stop the sweep.
    "search_confirm_frames": 3,
    # Give up on a search position (move to the next) after this many
    # camera frames without confirming, once arrived.
    "search_dwell_frames": 20,
    # Pan arrival tolerance is in degrees now (pan works directly in
    # degrees, no raw/tick scale -- see module docstring). Tilt still uses
    # its own raw-tick arrival check inline (AX-12A, unchanged mechanism).
    "search_arrival_tolerance_deg": 2.0,
    # If /xm430_node/new_position never confirms arrival within this many
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

        self.tilt_position_sub = None
        self.tilt_cmd_pub = None
        self.pan_position_sub = None
        self.pan_cmd_pub = None
        self._latest_tilt_position = None
        self._latest_pan_deg = None
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
            self.destroy_subscription(self.tilt_position_sub)
            self.destroy_publisher(self.tilt_cmd_pub)
            self.destroy_subscription(self.pan_position_sub)
            self.destroy_publisher(self.pan_cmd_pub)

            self.sub = None
            self.pose_pub = None
            self.tilt_position_sub = None
            self.tilt_cmd_pub = None
            self.pan_position_sub = None
            self.pan_cmd_pub = None
            self._latest_tilt_position = None
            self._latest_pan_deg = None
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
            # Note: unlike before, this is no longer precomputable -- how
            # many detections of a given color show up (and therefore how
            # many choose-and-order candidates exist) varies per frame now
            # that extra detections (reflections) are tolerated. See
            # _build_color_constrained_correspondences, called fresh each
            # frame.

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

            self.tilt_position_sub = self.create_subscription(
                MotorPosition,
                self.tilt_motor_topic,
                self._tilt_position_callback,
                10,
            )

            self.tilt_cmd_pub = self.create_publisher(
                MotorPosition,
                self.tilt_motor_cmd_topic,
                10,
            )

            self.pan_position_sub = self.create_subscription(
                Float64,
                self.pan_topic,
                self._pan_position_callback,
                10,
            )

            self.pan_cmd_pub = self.create_publisher(
                Float64,
                self.pan_cmd_topic,
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
                f"tilt via {self.tilt_motor_topic} -> {self.tilt_motor_cmd_topic}, "
                f"pan via {self.pan_topic} -> {self.pan_cmd_topic}"
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

            # Minimum, not exact -- see module docstring "Tolerating extra
            # detections per color". Fewer than the model needs of some
            # color means a partial/occluded view; skip. More is fine now
            # (reflections) -- handled below.
            if any(
                len(groups.get(color, [])) < count
                for color, count in self._required_color_counts.items()
            ):
                self.get_logger().warn(
                    "Not enough detections of some color this frame (need "
                    f"at least {self._required_color_counts}, got "
                    f"{ {c: len(v) for c, v in groups.items()} }). "
                    "Skipping frame.",
                    throttle_duration_sec=5.0,
                )
                self._update_pan_tilt_control(found_this_frame=False, mean_bearing=None)
                return

            # Safety valve against combinatorial blowup -- see
            # max_candidates_per_color's DEFAULTS comment. Keeps the
            # largest-area detections when a color has more candidates than
            # this.
            for color, dets in groups.items():
                if len(dets) > self.max_candidates_per_color:
                    dets.sort(key=lambda d: d.area_px, reverse=True)
                    groups[color] = dets[: self.max_candidates_per_color]

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
        constrained by color: for each color, choose-and-order exactly as
        many detections as the model has of that color out of however many
        showed up (itertools.permutations(dets, r) does "choose r out of
        len(dets), every order" directly -- no separate combinations step
        needed), then takes the Cartesian product across colors. With no
        extra detections this is the same 3! x 1! = 6 candidates as before;
        with reflections present it grows -- see module docstring
        "Tolerating extra detections per color".
        """
        colors = list(self._color_local_indices.keys())
        per_color_choices = [
            list(itertools.permutations(
                range(len(groups[color])), len(self._color_local_indices[color])
            ))
            for color in colors
        ]

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

    def _tilt_position_callback(self, msg: MotorPosition):
        self._latest_tilt_position = msg

    def _pan_position_callback(self, msg: Float64):
        # Wire format is radians (xm430_node's own convention) -- converted
        # to degrees immediately so the rest of this file (deadband,
        # search step, etc., all in degrees) never has to think about units.
        self._latest_pan_deg = float(np.degrees(msg.data))

    def _tilt_raw_to_deg(self, raw):
        return (raw - self.tilt_raw_center) * self.tilt_deg_per_raw

    def _tilt_deg_to_raw(self, deg):
        return self.tilt_raw_center + deg / self.tilt_deg_per_raw

    def _send_tilt_command(self, tilt_raw):
        """Publishes a 4-motor MotorPosition command, echoing back the 2
        drive motors' last known real values -- see module docstring, this
        is an absolute setpoint, not a per-motor delta."""

        if self._latest_tilt_position is None:
            self.get_logger().warn(
                f"Cannot send a tilt command yet -- no {self.tilt_motor_topic} "
                "feedback received, don't know the drive motors' current values.",
                throttle_duration_sec=5.0,
            )
            return

        cmd = MotorPosition()
        cmd.motor2 = self._latest_tilt_position.motor2
        cmd.motor3 = self._latest_tilt_position.motor3
        cmd.motor4 = self._latest_tilt_position.motor4
        setattr(cmd, self.tilt_motor_field,
                int(np.clip(tilt_raw, self.tilt_raw_min, self.tilt_raw_max)))

        self.tilt_cmd_pub.publish(cmd)

    def _send_pan_command(self, pan_deg):
        """Publishes a standalone Float64 (radians) to xm430_node -- no
        echo-back needed, unlike tilt, since pan doesn't share its topic
        with any other motor."""

        cmd = Float64()
        cmd.data = float(np.radians(np.clip(pan_deg, self.pan_min_deg, self.pan_max_deg)))
        self.pan_cmd_pub.publish(cmd)

    def _build_search_positions(self, start_at: str):
        """Pan positions (degrees) to sweep, search_step_deg apart, covering
        the full reachable range, starting from one edge. Always includes
        the far endpoint exactly even if the step doesn't divide evenly."""

        step_deg = self.search_step_deg

        if start_at == "min":
            positions = list(np.arange(self.pan_min_deg, self.pan_max_deg, step_deg))
            positions.append(self.pan_max_deg)
        else:
            positions = list(np.arange(self.pan_max_deg, self.pan_min_deg, -step_deg))
            positions.append(self.pan_min_deg)

        return [float(p) for p in positions]

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

        target_deg = self._search_positions[self._search_index]
        self._search_phase = "moving"
        self._arrival_wait_frames = 0
        self._send_pan_command(target_deg)
        self._send_tilt_command(self.tilt_home_raw)
        self.get_logger().info(
            f"LED-Suchlauf: naechste Pan-Position {target_deg:.1f} deg"
        )

    def _update_search(self, found_this_frame):
        current_pan_deg = self._latest_pan_deg

        if not self._search_exhausted and self._search_phase == "moving":
            target_deg = self._search_positions[self._search_index]
            self._arrival_wait_frames += 1
            arrived = abs(current_pan_deg - target_deg) <= self.search_arrival_tolerance_deg
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

        current_pan_deg = self._latest_pan_deg
        current_tilt_raw = getattr(self._latest_tilt_position, self.tilt_motor_field)

        new_pan_deg = None
        new_tilt_raw = None

        if abs(pan_dev_deg) > self.pan_deadband_deg:
            target_pan_deg = current_pan_deg + self.pan_correction_sign * pan_dev_deg

            if self.pan_min_deg <= target_pan_deg <= self.pan_max_deg:
                new_pan_deg = target_pan_deg
                self._pan_blocked = False
                self._pan_blocked_at_min = False
                self._pan_blocked_at_max = False
            else:
                # Would cross the 0/360 deg seam -- hold instead of
                # correcting (see module docstring: wraparound safety is
                # unconfirmed on this motor), remember which edge.
                self._pan_blocked = True
                self._pan_blocked_at_min = target_pan_deg < self.pan_min_deg
                self._pan_blocked_at_max = target_pan_deg > self.pan_max_deg
                self.get_logger().warn(
                    f"Pan-Korrektur wuerde ueber die 0/360-Grad-Naht fuehren "
                    f"(Ziel {target_pan_deg:.1f} deg, Bereich "
                    f"[{self.pan_min_deg}, {self.pan_max_deg}]) -- halte "
                    "Position, folge nicht weiter.",
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

        if new_pan_deg is not None:
            self._send_pan_command(new_pan_deg)
        if new_tilt_raw is not None:
            self._send_tilt_command(new_tilt_raw)

    def _update_pan_tilt_control(self, found_this_frame, mean_bearing):
        if self._latest_tilt_position is None or self._latest_pan_deg is None:
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
