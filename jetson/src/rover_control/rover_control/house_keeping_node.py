from asyncio.log import logger

import rclpy
from rclpy.node import Node

from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from rover_ws.jetson.src.rover_control.rover_control.logger_node import LoggerNode
class HousekeepingNode(Node):

    def __init__(self):
        super().__init__('housekeeping_node')

        # Subscriber für Log-Nachrichten
        self.subscription = self.create_subscription(
            DiagnosticArray,
            '/diagnostics',
            self.lidar_housekeeping_callback,
            10
        )


        self.get_logger().info('Housekeeping Node gestartet')


    def lidar_housekeeping_callback(self, msg):
        filename = 'log_housekeeping.csv'
# Gleiche für Realsense und Mono cam. Name vor DiagnosticArray ändern, damit man weiß, welche



def main(args=None):

    # ROS2 initialisieren
    rclpy.init(args=args)

    # Node erstellen
    node = HousekeepingNode()

    try:
        # Auf Nachrichten warten
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        # Node sauber beenden
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
