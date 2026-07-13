import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/workspaces/IRS_Rover_ROS2_Workspace/rover_ws/install/rover_lidar'
