import rclpy
from rclpy.node import Node

from rover_control_msgs.msg import LogMessage, Housekeeping

from . import log as logger   #(aufrufen der funktion durch logger.<function_name>)


class LoggerNode(Node):

    def __init__(self):
        super().__init__('logger_node')

        # Subscriber für Log-Nachrichten (jeweils eigene Variable)
        self.sub_operations = self.create_subscription(
            LogMessage,
            '/log/operations',
            self.log_operations_callback,
            10
        )

        self.sub_sensors = self.create_subscription(
            LogMessage,
            '/log/sensors',
            self.log_sensors_callback,
            10
        )

        self.sub_housekeeping = self.create_subscription(
            Housekeeping,
            '/log/housekeeping',
            self.log_housekeeping_callback,
            50
        )

        self.sub_wifi = self.create_subscription(
            LogMessage,
            '/log/wifi',
            self.log_wifi_callback,
            10
        )

        self.sub_com_stm = self.create_subscription(
            LogMessage,
            '/log/com_stm',
            self.log_com_stm_callback,
            10
        )

        self.get_logger().info('Logger Node gestartet')


    def log_operations_callback(self, msg):

        filename = 'log_operations.csv'

        # Nachricht an log.py weitergeben
        logger.write_log(
            filename,
            msg.source,
            msg.event,
            msg.message
        )

    def log_sensors_callback(self, msg):

        filename = 'log_sensors.csv'

        # Nachricht an log.py weitergeben
        logger.write_log(
            filename,
            msg.source,
            msg.event,
            msg.message
        )

    def log_housekeeping_callback(self, msg):

        filename = 'log_housekeeping.csv'

        # Housekeeping hat eigene Spalten -> eigene Funktion
        logger.write_housekeeping_data(
            filename,
            msg.source,
            msg.component,
            msg.type,
            msg.value
        )

    def log_wifi_callback(self, msg):

        filename = 'log_wifi.csv'

        # Nachricht an log.py weitergeben
        logger.write_log(
            filename,
            msg.source,
            msg.event,
            msg.message
        )

    def log_com_stm_callback(self, msg):

        filename = 'log_com_stm.csv'

        # Nachricht an log.py weitergeben
        logger.write_log(
            filename,
            msg.source,
            msg.event,
            msg.message
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