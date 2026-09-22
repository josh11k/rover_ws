from asyncio.log import logger
from time import time

import rclpy
from rclpy.node import Node

from diagnostic_msgs.msg import DiagnosticArray, DiagnosticStatus, KeyValue
from rover_control_msgs.msg import HousekeepingLog


class HousekeepingNode(Node):

    def __init__(self):
        super().__init__('housekeeping_node')

        self.period = 30.0  # Zeitintervall in Sekunden
        self.last_processed = 0.0  # Zeitstempel der letzten Verarbeitung

        # Subscriber für Log-Nachrichten
        self.subscription = self.create_subscription(
            DiagnosticArray,
            '/stereo/diagnostics',
            self.callback,
            10
        )

        # 3. Publisher für log
        self.publish_housekeeping_log = self.create_publisher(
            HousekeepingLog,
            '/log/housekeeping',
            10
        )


        self.get_logger().info('Housekeeping Node gestartet')

    def callback(self, msg: DiagnosticArray):
        now = time.monotonic()
        if now - self.last_processed < self.period:
            return
        self.last_processed = now

        self.stereo_housekeeping(msg)
        self.publish_jetson_temp()


    def stereo_housekeeping(self, msg: DiagnosticArray):


        for status in msg.status:
            # Optional: nur auf deine Kamera filtern
            # if status.hardware_id != '918512073905':
            #     continue

            if status.name.endswith('Temperatures'):
                temps = {}
                for kv in status.values:
                    try:
                        temps[kv.key] = float(kv.value)
                    except ValueError:
                        pass

                asic_temp = temps.get('Asic Temperature')
                projector_temp = temps.get('Projector Temperature')


                if asic_temp is not None:
                    msg_log = HousekeepingLog()  # oder wie deine Message-Klasse heißt
                    msg_log.source = "JETSON"
                    msg_log.component = "STEREO"
                    msg_log.type = "ASIC TEMPERATUR"
                    msg_log.value = str(asic_temp)  # ggf. Typ anpassen (float/int/str)
                    self.publish_housekeeping_log.publish(msg_log)

                if projector_temp is not None:
                    msg_log = HousekeepingLog()
                    msg_log.source = "JETSON"
                    msg_log.component = "STEREO"
                    msg_log.type = "PROJECTOR TEMPERATUR"
                    msg_log.value = str(projector_temp)
                    self.publish_housekeeping_log.publish(msg_log)

        

    
    def read_jetson_temp(self):
        max_temp = None
        for path in glob.glob('/sys/class/thermal/thermal_zone*/temp'):
            with open(path, 'r') as f:
                temp = int(f.read().strip()) / 1000.0
            if max_temp is None or temp > max_temp:
                max_temp = temp
        return max_temp


    def publish_jetson_temp(self):

        

        max_temp = self.read_jetson_temp()

        msg_log = HousekeepingLog()
        msg_log.source = "JETSON"
        msg_log.component = "JETSON"
        msg_log.type = "TEMPERATUR"
        msg_log.value = str(max_temp)
        self.publish_housekeeping_log.publish(msg_log)
            


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
