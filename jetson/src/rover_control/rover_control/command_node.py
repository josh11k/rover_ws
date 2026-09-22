from asyncio import subprocess
from tokenize import String

import rclpy
from rclpy.node import Node
import sys
import threading

# Uniform Service Interface
from rover_control_msgs.msg import OperationalMode, SystemRequest, LogMessage

class CommandNode(Node):
    def __init__(self):
        super().__init__('command_node')
        
        
        #Wait until the bridge node service is available in the network
        #while not self.client.wait_for_service(timeout_sec=1.0):
        #    self.get_logger().info('Waiting for STM bridge node service...')
            
        #self.get_logger().info('Connected to STM bridge node. Ready for commands.')

        # 1. Variablen
        self.state = "STANDBY"  # Initialer Modus

        # 2. Subsribers
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

        self.check_system_timer = self.create_timer(
            10.0, self.check_system_status
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
                # Neustart über systemctl (benötigt meist kein sudo für lokale User)
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
        self.publish_wifi.publish(String(data="get_status"))

    def check_system_status(self):
        i=1


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
            
            #if user_input.lower() == 'exit':
             #   break
                
            # Hier rufst du die Funktion aktiv mit der Eingabe auf!
            # node.send_mode_change_request(user_input)
            node.mode_feedback_callback(user_input)
            # node.send_mode_change_request(user_input)
            
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()