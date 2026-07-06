# All LED blobs detected in one mono-camera frame.
#
# header.stamp/frame_id are copied from the source image (frame_id =
# mono_cam_optical_frame), so detections can be time- and frame-correlated
# with everything else in the pipeline. Empty `detections` is a normal,
# valid message (no LEDs visible this frame) -- not an error condition.

std_msgs/Header header
LedDetection[] detections
