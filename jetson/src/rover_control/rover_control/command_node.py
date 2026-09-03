import rclpy
from rclpy.node import Node
import sys
import threading

# Uniform Service Interface
from rover_control_msgs.srv import SetOperationalMode as SetModeSrv
from rover_control_msgs.msg import SetOperationalMode as SetModeMsg 
from rover_control_msgs.msg import CurrentOperationalMode

class CommandNode(Node):
    def __init__(self):
        super().__init__('command_node')
        
        # Create a client for the service provided by STMBridgeNode
        self.client = self.create_client(
            SetModeSrv, 
            '/stm/set_mode_on_stm')
        
        #Wait until the bridge node service is available in the network
        #while not self.client.wait_for_service(timeout_sec=1.0):
        #    self.get_logger().info('Waiting for STM bridge node service...')
            
        #self.get_logger().info('Connected to STM bridge node. Ready for commands.')

        # Subscribe to the feedback topic from STMBridgeNode
        self.subscription = self.create_subscription(
            SetModeMsg, 
            '/stm/feedback_of_stm', 
            self.mode_feedback_callback,
              10)  
        
        self.publisher = self.create_publisher(
            CurrentOperationalMode, 
            '/operational_mode/current',
              10)
        
    # Com to STM: Sends a request to the STMBridgeNode to change the operational mode of the STM32
    def send_mode_change_request(self, target_mode):
        """Sends an asynchronous service request to the bridge node"""
        # 1. Instantiate and fill the request object
        request = SetModeSrv.Request()
        request.mode = target_mode
        
        self.get_logger().info(f"Sending mode change request: '{target_mode}'")
        
        # 2. Asynchronous call to prevent freezing the executor thread
        future = self.client.call_async(request)
        
        # 3. Register a callback that fires once the bridge responds
        future.add_done_callback(self.mode_response_callback)

    # Com to STM:Checks if mode change was successful
    def mode_response_callback(self, future):
        """Triggered automatically when the bridge node returns the hardware feedback"""
        try:
            response = future.result()
            
            if response.success:
                self.get_logger().info(f"SUCCESS: {response.message}")
                # PLACE YOUR CAMERA TRIGGER LOGIC HERE
            else:
                self.get_logger().error(f"FAILED: {response.message}")
                
        except Exception as e:
            self.get_logger().error(f"Service call failed with exception: {e}")
   
    # Com to STM: Reads out the new operational mode requested by the STM32 
    def mode_feedback_callback(self, input):
        msg = CurrentOperationalMode()
        msg.mode = input  # Assuming the message is a simple string for this example
        #msg = input.mode  # If the message is a custom message type, adjust accordingly

        """Triggered whenever the bridge node publishes a feedback message"""
        self.get_logger().info(f"Feedback from STM: Current mode is '{msg.mode}'")
        if msg.mode == "STANDBY":
            self.get_logger().info("STM32 requests to switch to STANDBY mode.")
            self.publisher.publish(msg)  # Publish the feedback to the /operational_mode/current topic
        elif msg.mode == "PERCEPTION":
            self.get_logger().info("STM32 requests to switch to PERCEPTION mode.")
            self.publisher.publish(msg)  # Publish the feedback to the /operational_mode/current topic
        elif msg.mode == "SAFE":
            self.get_logger().info("STM32 requests to switch to SAFE mode.")
            self.publisher.publish(msg)  # Publish the feedback to the /operational_mode/currents topic
        else:
            self.get_logger().error(f"Unknown mode received: {msg.mode}")
        


def main(args=None):
    rclpy.init(args=args)
    node = CommandNode()
    
    # Startet das ROS2-Spinning in einem eigenen Hintergrund-Thread
    spin_thread = threading.Thread(target=rclpy.spin, args=(node,), daemon=True)
    spin_thread.start()
    
    node.get_logger().info("System bereit. Gib einen Modus ein (z.B. 00, 01, 02) oder 'exit' zum Beenden:")
    
    try:
        while rclpy.ok():
            # Warte auf Eingabe im Terminal
            user_input = input("Target Mode: ").strip()
            
            if user_input.lower() == 'exit':
                break
                
            # Hier rufst du die Funktion aktiv mit der Eingabe auf!
            # node.send_mode_change_request(user_input)
            node.mode_feedback_callback(user_input)
            
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()