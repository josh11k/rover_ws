import rclpy
from rclpy.node import Node

from rover_control_msgs.msg import LogMessage, Housekeeping

from . import log as logger   #(aufrufen der funktion durch logger.<function_name>)


class LoggerNode(Node):

    def __init__(self):
        super().__init__('logger_node')

        # Subscriber für Log-Nachrichten
        self.subscription = self.create_subscription(
            LogMessage,
            '/log/operations',
            self.log_operations_callback,
            10
        )

        self.subscription = self.create_subscription(
            LogMessage,
            '/log/sensors',
            self.log_sensors_callback,
            10
        )

        self.subscription = self.create_subscription(
            Housekeeping,
            '/log/housekeeping',
            self.log_housekeeping_callback,
            50
        )

        self.subscription = self.create_subscription(
            LogMessage,
            '/log/wifi',
            self.log_wifi_callback,
            10
        )

        self.subscription = self.create_subscription(
            LogMessage,
            '/log/com_stm',
            self.log_com_stm_callback,
            10
        )

        self.get_logger().info('Logger Node gestartet')


    def log_operations_callback(self, msg):

        filename = '~/rover_log/log_operations.csv'

        # Nachricht an logger.py weitergeben
        log.write_log(
            filename,
            msg.source,
            msg.event,
            msg.details
        )

    def log_sensors_callback(self, msg):

        filename = '~/rover_log/log_sensors.csv'

        # Nachricht an logger.py weitergeben
        log.write_log(
            filename,
            msg.source,
            msg.event,
            msg.details
        )

    def log_housekeeping_callback(self, msg):

        filename = '~/rover_log/log_housekeeping.csv'

        # Nachricht an logger.py weitergeben
        log.write_log(
            filename,
            msg.source,
            msg.component,
            msg.value
        )

    def log_wifi_callback(self, msg):

        filename = '~/rover_log/log_wifi.csv'

        # Nachricht an logger.py weitergeben
        log .write_log(
            filename,
            msg.source,
            msg.event,
            msg.details
        )

    def log_com_stm_callback(self, msg):

        filename = '~/rover_log/log_com_stm.csv'

        # Nachricht an logger.py weitergeben
        log.write_log(
            filename,
            msg.source,
            msg.event,
            msg.details
        )


def main(args=None):

    # ROS2 initialisieren
    rclpy.init(args=args)

    # Node erstellen
    node = LoggerNode()

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
