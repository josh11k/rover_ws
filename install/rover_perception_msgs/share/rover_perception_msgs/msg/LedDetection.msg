# A single LED blob detected in a mono-camera image by led_detector_node.

float32 pixel_u          # blob centroid, image x (pixels)
float32 pixel_v          # blob centroid, image y (pixels)
uint32  area_px          # blob size, connected-component pixel count

uint8   color_r          # mean color of the blob (0-255) -- lets a future
uint8   color_g          # consumer match a detection to a known robot's
uint8   color_b          # LED color, if robots use distinct colors

# Unit bearing vector to the blob, in the camera's optical frame (REP-103:
# Z forward, X right, Y down). Pre-converted from (pixel_u, pixel_v) via the
# camera intrinsics, so downstream nodes can rotate it into base_link with
# the same static TF used for the point clouds, without needing pixel
# coordinates or intrinsics again. A mono camera alone only gives a
# *direction*, not a distance -- turning this into a full 3D position needs
# extra information (e.g. known LED spacing, or multi-view triangulation),
# which is out of scope for this node.
geometry_msgs/Vector3 bearing
