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
<<<<<<< HEAD
            10)  
=======
            10)
>>>>>>> 1f574e34b3dd02bb140180baa723fae6e2293a4d

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

<<<<<<< HEAD
        self.check_system_timer = self.create_timer(
            10.0, self.check_system_status
=======
        self.get_logger().info(
            "command_node bereit -- Steuerung ausschliesslich ueber "
            "/bridge_node/system_request (SET_STATE / REBOOT / SHUTDOWN)."
>>>>>>> 1f574e34b3dd02bb140180baa723fae6e2293a4d
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
        self.publish_wifi.publish(String(data="get_status"))

    def check_system_status(self):
        i=1



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