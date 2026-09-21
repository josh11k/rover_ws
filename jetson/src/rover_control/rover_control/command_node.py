import subprocess

import rclpy
from rclpy.node import Node

# Uniform Service Interface
from rover_control_msgs.msg import OperationalMode, SystemRequest, LogMessage
from std_msgs.msg import String


class CommandNode(Node):
    def __init__(self):
        super().__init__('command_node')

        # 1. Variablen
        self.state = "STANDBY"  # Initialer Modus

        # 2. Subscribers
        self.subscribe_bridge_node = self.create_subscription(
            SystemRequest,
            '/bridge_node/system_request',
            self.bridge_node_callback,
            10)

        # 3. Publishers
        self.publish_operational_mode = self.create_publisher(
            OperationalMode,
            '/operational_mode/current',
            10)

        self.publish_system_request = self.create_publisher(
            SystemRequest,
            '/command/system_request',
            10
        )

        self.publish_operational_log = self.create_publisher(
            LogMessage,
            '/log/operations',
            10
        )

        self.publish_wifi_log = self.create_publisher(
            LogMessage,
            '/log/wifi',
            10
        )

        self.publish_com_stm_log = self.create_publisher(
            LogMessage,
            '/log/com_stm',
            10
        )

        self.publish_trigger_hkd = self.create_publisher(
            String,
            '/trigger/housekeeping',
            10
        )

        self.publish_wifi = self.create_publisher(
            String,
            '/trigger/wifi',
            10
        )

        # 4. Timer
        self.housekeeping_timer = self.create_timer(
            60.0, self.trigger_housekeeping
        )

        self.alive_timer = self.create_timer(
            5.0, self.send_alive_message
        )

        self.get_logger().info(
            "command_node bereit -- Steuerung ausschliesslich ueber "
            "/bridge_node/system_request (SET_STATE / REBOOT / SHUTDOWN)."
        )

    def bridge_node_callback(self, msg):

        if msg.task == "SET_STATE":
            msg_state = OperationalMode()
            msg_state.mode = msg.message  # Ergebnis: "STANDBY"

            msg_log = LogMessage()
            msg_log.source = "JETSON"
            msg_log.event = "INFO"
            msg_log.details = f"Changing mode to from {self.state} to {msg.message}"

            self.state = msg.message  # Update the internal state
            self.publish_operational_mode.publish(msg_state)
            self.publish_operational_log.publish(msg_log)

        if msg.task == "REBOOT":
            try:
                self.publish_operational_log.publish(LogMessage(source="JETSON", event="INFO", details="Rebooting system..."))
                subprocess.run(['systemctl', 'reboot'], check=True)
            except subprocess.CalledProcessError as e:
                self.publish_operational_log.publish(LogMessage(source="JETSON", event="ERROR", details=f"Reboot failed: {e}"))

        if msg.task == "SHUTDOWN":
            try:
                self.publish_operational_log.publish(LogMessage(source="JETSON", event="INFO", details="Shutting down system..."))
                subprocess.Popen(['systemctl', 'poweroff'])
            except Exception as e:
                self.publish_operational_log.publish(LogMessage(source="JETSON", event="ERROR", details=f"Shutdown failed: {e}"))

    def trigger_housekeeping(self):

        msg = LogMessage()
        msg.source = "JETSON"
        msg.event = "INFO"
        msg.details = "Request to aquire house keeping data."

        self.publish_operational_log.publish(msg)
        self.publish_trigger_hkd.publish(String(data="trigger"))

    def send_alive_message(self):

        msg_log = LogMessage()
        msg_log.source = "JETSON"
        msg_log.event = "INFO"
        msg_log.details = "System is alive and operational."

        msg_system = SystemRequest()
        msg_system.source = "JETSON"
        msg_system.task = "ALIVE"
        msg_system.message = self.state

        self.publish_operational_log.publish(msg_log)
        self.publish_system_request.publish(msg_system)

    # Com to STM: Sends a request to the STMBridgeNode to change the operational mode of the STM32
    '''def send_mode_change_request(self, target_mode):
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
        msg = OperationalMode()
        msg.mode = input #.mode  # Assuming the message is a simple string for this example
        #msg = input.mode  # If the message is a custom message type, adjust accordingly

        """Triggered whenever the bridge node publishes a feedback message"""
        self.get_logger().info(f"Feedback from STM: Current mode is '{msg.mode}'")
        if msg.mode == "STANDBY":
        
            self.get_logger().info("STM32 requests to switch to STANDBY mode.")
            self.publisher.publish(msg)  # Publish the feedback to the /operational_mode/current topic
        elif msg.mode == "PERCEPTION":

            self.get_logger().info("STM32 requests to switch to PERCEPTION mode.")
            self.publisher.publish(msg)  # Publish the feedback to the /operational_mode/current topic
        #elif msg.mode == "SAFE":
         #   self.get_logger().info("STM32 requests to switch to SAFE mode.")
          #  self.publisher.publish(msg)  # Publish the feedback to the /operational_mode/currents topic
        else:
            self.get_logger().error(f"Unknown mode received: {msg.mode}")
        
'''


def main(args=None):
    rclpy.init(args=args)
    node = CommandNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()