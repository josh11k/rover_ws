"""Visualize the terrain elevation grid in RViz2.

Converts the custom TerrainGrid message (see rover_perception_msgs, no RViz
plugin exists for it) into a standard sensor_msgs/PointCloud2 with an
"intensity" field -- something RViz2's built-in PointCloud2 display already
knows how to render, no custom plugin needed.

One point per valid grid cell (skipped if mean_z is NaN, i.e. the cell had
too few points to be trusted -- see terrain_analysis.py / obstacle_grid_node):

    x, y      = cell center, computed from info.origin + resolution * index
    z         = mean_z (real elevation in meters, not normalized/clamped)
    intensity = whichever field `color_field` selects (default: mean_z,
                also available: roughness, plane_slope_deg, traversability)

z is always the real height regardless of color_field, so switching
color_field only changes what the color represents, not the cell's height
in the view.

RViz2 setup: add a PointCloud2 display on /terrain/elevation_cloud (Fixed
Frame must include mast_base_link in its TF tree, already provided by
mast_pose_node), set Color Transformer to "Intensity", and Style to
"Squares" or "Boxes" with Size ~= the grid's resolution (0.25 m by default)
for a filled, cell-like look instead of sparse points.
"""

import numpy as np

import rclpy
from rclpy.node import Node

from sensor_msgs.msg import PointCloud2, PointField
import sensor_msgs_py.point_cloud2 as pc2

from rover_perception_msgs.msg import TerrainGrid


ELEVATION_FIELDS = [
    PointField(name="x", offset=0, datatype=PointField.FLOAT32, count=1),
    PointField(name="y", offset=4, datatype=PointField.FLOAT32, count=1),
    PointField(name="z", offset=8, datatype=PointField.FLOAT32, count=1),
    PointField(name="intensity", offset=12, datatype=PointField.FLOAT32, count=1),
]

VALID_COLOR_FIELDS = ("mean_z", "roughness", "plane_slope_deg", "traversability")


DEFAULTS = {
    "input_topic": "/terrain/terrain_grid_stats",
    "output_topic": "/terrain/elevation_cloud",
    # Which TerrainGrid field feeds the "intensity" channel (RViz Color
    # Transformer). Cell height (z) is always mean_z regardless of this.
    "color_field": "mean_z",
}


class TerrainVisualizationNode(Node):

    def __init__(self):
        super().__init__("terrain_visualization_node")

        self._declare_parameters()
        self._load_parameters()

        if self.color_field not in VALID_COLOR_FIELDS:
            self.get_logger().warn(
                f"Unknown color_field '{self.color_field}', "
                f"falling back to 'mean_z'. Valid options: {VALID_COLOR_FIELDS}"
            )
            self.color_field = "mean_z"

        self.sub = self.create_subscription(
            TerrainGrid,
            self.input_topic,
            self.grid_callback,
            10,
        )

        self.pub = self.create_publisher(
            PointCloud2,
            self.output_topic,
            10,
        )

        self.get_logger().info(
            f"terrain_visualization_node: {self.input_topic} -> "
            f"{self.output_topic} (color_field={self.color_field})"
        )

    def _declare_parameters(self):
        for name, value in DEFAULTS.items():
            self.declare_parameter(name, value)

    def _load_parameters(self):
        for name in DEFAULTS:
            setattr(self, name, self.get_parameter(name).value)

    def grid_callback(self, msg: TerrainGrid):
        try:
            width = msg.info.width
            height = msg.info.height
            resolution = msg.info.resolution
            origin_x = msg.info.origin.position.x
            origin_y = msg.info.origin.position.y

            n = width * height
            mean_z = np.array(msg.mean_z, dtype=np.float32)

            if mean_z.size != n:
                self.get_logger().error(
                    f"mean_z size {mean_z.size} != width*height {n}, "
                    "skipping this grid.",
                    throttle_duration_sec=5.0,
                )
                return

            color_by_field = {
                "mean_z": mean_z,
                "roughness": np.array(msg.roughness, dtype=np.float32),
                "plane_slope_deg": np.array(msg.plane_slope_deg, dtype=np.float32),
                "traversability": np.array(msg.traversability, dtype=np.float32),
            }
            color_values = color_by_field[self.color_field]

            # A cell is "valid" (has real elevation data) iff mean_z isn't
            # NaN -- see flatten_elevation_grid(). traversability uses -1
            # (not NaN) as its own "unknown" sentinel, so it needs a
            # separate check when it's the chosen color field.
            valid = np.isfinite(mean_z)
            if self.color_field == "traversability":
                valid &= (color_values != -1)
            else:
                valid &= np.isfinite(color_values)

            if not np.any(valid):
                return

            indices = np.nonzero(valid)[0]
            ix = (indices % width).astype(np.float32)
            iy = (indices // width).astype(np.float32)

            x = origin_x + (ix + 0.5) * resolution
            y = origin_y + (iy + 0.5) * resolution
            z = mean_z[indices]
            intensity = color_values[indices].astype(np.float32)

            points = np.stack([x, y, z, intensity], axis=-1).astype(np.float32)

            cloud_msg = pc2.create_cloud(msg.header, ELEVATION_FIELDS, points)
            self.pub.publish(cloud_msg)

        except Exception as exc:  # noqa: BLE001 - keep the node alive
            self.get_logger().error(f"grid_callback failed: {exc}")


def main(args=None):
    rclpy.init(args=args)

    node = TerrainVisualizationNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
