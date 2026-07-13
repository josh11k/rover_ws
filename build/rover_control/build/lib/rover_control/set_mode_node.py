import rclpy
from rclpy.node import Node
from rover_control_msgs.msg import  OperationalModeSettings, CurrentOperationalMode



class OperationalModes(Node):
    """Class to define the operational modes of the system"""
    
    #STANDBY = "00"
    #PERCEPTION = "01"
    #SAFE = "02"

    def __init__(self):

        super().__init__('set_mode_node')

        self.declare_parameter('current_mode',"STANDBY")
        self.declare_parameter('mono_cam', "OFF")
        self.declare_parameter('stereo_cam', "OFF")
        self.declare_parameter('lidar', "OFF")

        self.subscription = self.create_subscription(
            CurrentOperationalMode, 
            '/operational_mode/current', 
            self.set_operational_mode_callback,
              10)
        
        self.publisher = self.create_publisher(
            OperationalModeSettings, 
            '/operational_mode/settings',
              10)

        
    # Changes the current state of the mono cam   

    def set_operational_mode_callback(self, current_mode):
        
        msg = OperationalModeSettings()
        mode = current_mode.mode

        if mode == "STANDBY":
            msg.stereo_cam = "STANDBY"
            msg.mono_cam = "STANDBY"
            msg.lidar = "STANDBY"   
        
        elif mode == "PERCEPTION":
            msg.stereo_cam = "ON"
            msg.mono_cam = "ON"
            msg.lidar = "ON"    
        
        elif mode == "SAFE":
            msg.stereo_cam = "OFF"
            msg.mono_cam = "OFF"        
            msg.lidar = "OFF"

        self.get_logger().info(f"Stereo camera set to: {msg.stereo_cam}")
        self.get_logger().info(f"Mono camera set to: {msg.mono_cam}")
        self.get_logger().info(f"LiDAR set to: {msg.lidar}")

        self.publisher.publish(msg)

def main(args=None):

    rclpy.init(args=args)
    node = OperationalModes()
    
    try:

        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("Operational Modes Node stopped")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()

         




