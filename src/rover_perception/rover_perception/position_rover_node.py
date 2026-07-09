"""Solve the rover's pose (position + orientation) in the world frame from
led_detector_node's LED-blob detections -- the diagram's "position_rover_node",
the final consumer of the mono-cam/LED branch.

Physical setup (see fake_mono_camera_node.py's docstring): a fixed
mast-mounted camera observes a separate rover carrying 3 rigid LED panels
(roof/left/right, one solid color each -- green/red/blue), each shaped as
an isosceles triangle (2 legs + a base) plus a 4th LED partway along one
leg. Every frame, only the panel(s) currently facing the camera are lit.

This is a PnP problem (Perspective-n-Point) solved per panel: given known
3D points in that panel's own local frame and their observed bearing rays
(unit vectors) in the camera's optical frame, solve for the rigid transform
(rotation + translation) from panel-local to camera-optical. led_detector_node
gives us bearings and a mean color per blob; it does NOT tell us *which*
detected blob is which specific LED on the panel -- that correspondence
problem, plus grouping detections into panels and turning a solved panel
pose into a *rover* pose, is what this node does.

No OpenCV, consistent with led_detector_node's own from-scratch approach:

1. Classify each detection into a panel (roof/green, left/red, right/blue)
   by its dominant color channel (color_r/g/b, from led_detector_node).
   Detections that don't form a clean group of exactly 4 for some panel are
   ignored -- a partial view of a panel (occlusion, a missed blob) isn't
   enough to solve that panel's pose.

2. For each panel with exactly 4 detections: because the panel's 4-LED
   shape (triangle + 1 leg point) has NO rotational or mirror symmetry --
   unlike the old symmetric square+center pattern this replaced -- every
   one of the 24 possible pairings (4! permutations) between the 4 detected
   bearings and the panel's 4 known local points is tried, and whichever
   one produces the best-fitting pose is kept. This is exhaustive and
   exact: exactly one of the 24 pairings is the true correspondence, and
   because the pattern is asymmetric, that pairing's fit is unambiguously
   better than all 23 wrong ones (this is the whole point of choosing an
   asymmetric shape -- see the chat discussion that led to this design).
   This also means, unlike the old pattern, there is no leftover yaw
   ambiguity: a correct fit pins down the panel's (and therefore the
   rover's) full orientation, not just its position and tilt.

3. For a given candidate correspondence, the actual 6-DOF pose (rotation +
   translation, camera <- panel) is found via nonlinear least squares
   (scipy.optimize.least_squares) minimizing the difference between
   predicted and observed unit bearings. A few different initial yaw
   guesses are tried per candidate purely to help the optimizer avoid bad
   local minima for large rotations -- cheap, since each solve only has 4
   points.

4. Whichever (panel x correspondence x yaw-seed) attempt converges to the
   lowest residual, *per panel*, is kept as that panel's candidate pose. If
   more than one panel produced a valid detection set this frame (e.g. the
   rover is seen at an angle where two panels are both edge-on visible),
   the panel with the lowest residual is used -- more views isn't better
   here, a clean single-panel fit is more trustworthy than an ambiguous
   one. If even the best panel's residual is too large
   (max_fit_residual_deg), the frame is dropped rather than publishing a
   bad pose.

5. The winning panel's solved pose (camera <- panel) is composed with that
   panel's known, fixed mounting extrinsics (position + orientation
   relative to the rover's own center -- see the DEFAULTS below) to get
   the pose of the *rover center* in the camera frame, camera <- rover.
   This is the step that's new compared to the single-tag version: a
   solved LED pattern pose is no longer directly the rover's pose, it's
   one panel's pose, and has to be translated back to "where is the rover,
   given that this is where its roof/left/right panel is".

6. That camera <- rover pose is transformed into the world frame using the
   existing TF tree (world -> mast_base_link -> mast_platform_link ->
   mono_cam_optical_frame, built by mast_pose_node + the static camera-mount
   transform) and published as a standard geometry_msgs/PoseStamped, plus
   broadcast as a TF (world -> rover_frame) so it shows up in RViz2 like
   everything else in this project.

Placeholder values throughout (panel shape/size, panel mounting positions
and orientations relative to rover center) -- MUST be kept in sync with
fake_mono_camera_node's matching DEFAULTS and its hardcoded
right_axis/up_axis/normal triples (see that node's docstring for why),
since there's no shared source of truth for these yet. Replace both with
real measurements once the rover's physical LED mounts are finalized.
"""

import itertools

import numpy as np

import rclpy
from rclpy.node import Node
from rclpy.duration import Duration

from geometry_msgs.msg import PoseStamped, TransformStamped

import tf2_ros
from scipy.spatial.transform import Rotation
from scipy.optimize import least_squares

from rover_perception_msgs.msg import LedDetectionArray


DEFAULTS = {
    "detections_topic": "/mono_cam/led_detections",
    "pose_topic": "/rover/estimated_pose",
    "world_frame": "world",
    # TF child frame this node broadcasts for the solved rover pose, purely
    # for RViz2 visualization -- not consumed by any other node (yet).
    "rover_frame": "rover_estimated_link",

    # Shared LED-panel shape (all 3 panels use the same asymmetric
    # geometry): isosceles triangle (2 legs of panel_leg_m, base of
    # panel_base_m) + a 4th LED at panel_extra_led_fraction along ONE leg
    # (0 = at the base corner, 1 = at the apex). MUST match
    # fake_mono_camera_node's DEFAULTS exactly.
    "panel_base_m": 0.20,
    "panel_leg_m": 0.25,
    "panel_extra_led_fraction": 0.5,

    # Placeholder panel mounting relative to the rover's own center (before
    # the rover's yaw is applied). MUST match fake_mono_camera_node's
    # DEFAULTS exactly -- and its hardcoded right_axis/up_axis/normal
    # triples in __init__ below must match that node's too.
    "roof_height_offset_m": 0.20,
    "side_offset_m": 0.15,
    "side_height_offset_m": 0.05,

    # A panel needs exactly this many same-colored detections to attempt a
    # solve (all 4 of its LEDs, no partial fits from a partially occluded
    # panel).
    "min_detections": 4,

    # If the best panel's RMS bearing residual (converted to an
    # approximate angle) exceeds this, the frame is dropped as unreliable
    # rather than publishing a bad pose.
    "max_fit_residual_deg": 3.0,

    "tf_timeout_sec": 0.3,
}

# Yaw seeds (degrees, rotation about the camera/world "up"-ish Y axis) tried
# per correspondence candidate, purely to help the nonlinear solver avoid a
# bad local minimum for large rotations -- see module docstring point 3.
_SEED_YAW_DEG = (0.0, 90.0, 180.0, 270.0)


def _build_panel_local_points(base_m: float, leg_m: float, extra_fraction: float) -> np.ndarray:
    """The shared 4-LED panel shape, as 3D points in the panel's own local
    frame (x=along right_axis, y=along up_axis, z=0 -- the panel is flat).
    Mirrors fake_mono_camera_node's _build_panel_local_points (2D) -- kept
    as a separate copy since this workspace has no shared-constants module
    yet; the two MUST be kept in sync (base_m/leg_m/extra_fraction here come
    from this node's own DEFAULTS, meant to match the other node's).
    """
    half_base = base_m / 2.0
    apex_height = float(np.sqrt(max(leg_m ** 2 - half_base ** 2, 1e-9)))

    base_left = np.array([-half_base, 0.0, 0.0])
    base_right = np.array([half_base, 0.0, 0.0])
    apex = np.array([0.0, apex_height, 0.0])
    extra = base_left + extra_fraction * (apex - base_left)

    return np.array([base_left, base_right, apex, extra])  # (4, 3)


def _mount_rotation(right_axis: np.ndarray, up_axis: np.ndarray, normal: np.ndarray) -> np.ndarray:
    """Panel-local -> rover-local rotation matrix, built from the panel's
    own basis vectors (as columns). right_axis/up_axis/normal must form a
    proper (determinant +1) orthonormal basis, i.e. normal = right x up --
    see fake_mono_camera_node's docstring for why this matters.
    """
    return np.column_stack([right_axis, up_axis, normal])


class PositionRoverNode(Node):

    def __init__(self):
        super().__init__("position_rover_node")

        self._declare_parameters()
        self._load_parameters()

        self._local_points = _build_panel_local_points(
            self.panel_base_m, self.panel_leg_m, self.panel_extra_led_fraction
        )

        # Per-panel mounting extrinsics relative to the rover center --
        # MUST match fake_mono_camera_node's panel definitions (mount
        # offsets AND right_axis/up_axis/normal triples) exactly.
        self._panel_extrinsics = {
            "roof": {
                "mount_offset": np.array([0.0, self.roof_height_offset_m, 0.0]),
                "R_mount": _mount_rotation(
                    np.array([1.0, 0.0, 0.0]),
                    np.array([0.0, 0.0, -1.0]),
                    np.array([0.0, 1.0, 0.0]),
                ),
            },
            "left": {
                "mount_offset": np.array([-self.side_offset_m, self.side_height_offset_m, 0.0]),
                "R_mount": _mount_rotation(
                    np.array([0.0, 0.0, 1.0]),
                    np.array([0.0, 1.0, 0.0]),
                    np.array([-1.0, 0.0, 0.0]),
                ),
            },
            "right": {
                "mount_offset": np.array([self.side_offset_m, self.side_height_offset_m, 0.0]),
                "R_mount": _mount_rotation(
                    np.array([0.0, 0.0, -1.0]),
                    np.array([0.0, 1.0, 0.0]),
                    np.array([1.0, 0.0, 0.0]),
                ),
            },
        }

        self._seed_rotvecs = [
            Rotation.from_euler("y", deg, degrees=True).as_rotvec()
            for deg in _SEED_YAW_DEG
        ]

        # All 4! = 24 possible pairings between (ordered) detected bearings
        # and the panel's 4 local points -- see module docstring point 2.
        self._correspondence_perms = list(itertools.permutations(range(4)))

        self.tf_buffer = tf2_ros.Buffer()
        self.tf_listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.tf_broadcaster = tf2_ros.TransformBroadcaster(self)

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

        self.get_logger().info(
            f"position_rover_node: {self.detections_topic} -> "
            f"{self.pose_topic} (world_frame={self.world_frame}, "
            f"3 panels [roof=green, left=red, right=blue], "
            f"panel_base_m={self.panel_base_m}, panel_leg_m={self.panel_leg_m})"
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
                return

            groups = {"roof": [], "left": [], "right": []}
            for d in msg.detections:
                panel_name = self._classify_panel(d.color_r, d.color_g, d.color_b)
                groups[panel_name].append(d)

            best = None  # (rms_deg, panel_name, rotmat_cam_rover, t_cam_rover)

            for panel_name, dets in groups.items():
                if len(dets) != 4:
                    continue

                bearings = np.array([
                    (d.bearing.x, d.bearing.y, d.bearing.z) for d in dets
                ], dtype=np.float64)
                bearings = bearings / np.linalg.norm(bearings, axis=1, keepdims=True)

                t_seed = self._initial_translation_guess(bearings, self._local_points)
                result = self._search_best_pose(bearings, self._local_points, t_seed)
                if result is None:
                    continue

                rms_deg, rotmat_cam_panel, t_cam_panel = result
                if rms_deg > self.max_fit_residual_deg:
                    continue

                extrinsics = self._panel_extrinsics[panel_name]
                rotmat_cam_rover, t_cam_rover = self._compose_rover_pose(
                    rotmat_cam_panel, t_cam_panel, extrinsics
                )

                if best is None or rms_deg < best[0]:
                    best = (rms_deg, panel_name, rotmat_cam_rover, t_cam_rover)

            if best is None:
                self.get_logger().warn(
                    "No panel (roof/left/right) produced a valid 4-LED fit "
                    f"this frame ({n} total detections, "
                    f"roof={len(groups['roof'])} left={len(groups['left'])} "
                    f"right={len(groups['right'])}). Skipping frame.",
                    throttle_duration_sec=5.0,
                )
                return

            rms_deg, panel_name, rotmat_cam_rover, t_cam_rover = best
            self._publish_world_pose(msg, rotmat_cam_rover, t_cam_rover)

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"detections_callback failed: {exc}")

    # ------------------------------------------------------------------
    # Panel classification
    # ------------------------------------------------------------------
    def _classify_panel(self, r: float, g: float, b: float) -> str:
        """Which panel a detection belongs to, by its dominant color
        channel (roof=green, left=red, right=blue -- see
        fake_mono_camera_node's panel colors). led_detector_node has
        already filtered out low-dominance/ambiguous blobs, so this just
        picks the highest of the 3 channels.
        """
        idx = int(np.argmax([r, g, b]))
        return ("left", "roof", "right")[idx]

    # ------------------------------------------------------------------
    # Pose search
    # ------------------------------------------------------------------
    def _initial_translation_guess(self, bearings: np.ndarray, local_points: np.ndarray) -> np.ndarray:
        """Rough initial distance estimate from the panel's known size and
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

    def _search_best_pose(self, bearings, local_points, t_seed):
        """Tries every (24-permutation correspondence x yaw seed)
        combination, returns (rms_residual_deg, rotation_matrix,
        translation) [camera <- panel] for whichever converged to the
        lowest cost, or None if nothing did.
        """
        best_cost = None
        best_result = None

        for perm in self._correspondence_perms:
            candidate = bearings[list(perm)]

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
    # Panel pose -> rover-center pose
    # ------------------------------------------------------------------
    def _compose_rover_pose(self, rotmat_cam_panel, t_cam_panel, extrinsics):
        """Given a solved camera<-panel pose and that panel's fixed
        mounting extrinsics (rover-local rotation + offset), returns the
        camera<-rover pose.

        Derivation: a point on the panel satisfies both
            X_camera = rotmat_cam_panel @ X_panel + t_cam_panel
            X_panel  = R_mount.T @ (X_rover - mount_offset)
        (the second line just inverts "X_rover = mount_offset +
        R_mount @ X_panel", the panel's placement relative to the rover
        center). Substituting gives X_camera = R_cr @ X_rover + t_cr with:
            R_cr = rotmat_cam_panel @ R_mount.T
            t_cr = t_cam_panel - rotmat_cam_panel @ R_mount.T @ mount_offset
        which is exactly the rover center's pose in the camera frame (at
        X_rover = 0, X_camera = t_cr).
        """
        R_mount = extrinsics["R_mount"]
        mount_offset = extrinsics["mount_offset"]

        rotmat_cam_rover = rotmat_cam_panel @ R_mount.T
        t_cam_rover = t_cam_panel - rotmat_cam_panel @ R_mount.T @ mount_offset

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
