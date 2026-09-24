import subprocess
import time

import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

# Uniform Service Interface
from rover_control_msgs.msg import OperationalMode, SystemRequest, LogMessage
from std_msgs.msg import String
from std_srvs.srv import Trigger


class CommandNode(Node):
    def __init__(self):
        super().__init__('command_node')

        # 1. Variablen
        self.state = "STANDBY"  # Initialer Modus
        self.old_state = "STANDBY"  # Initialer alter Modus
        self.wedges = 0
        self.max_wedges = 3          # Anzahl Wedges pro Mapping-Session -- anpassen
        self.mapping_timer = None    # nur aktiv, solange state == MAPPING
        self.wedges_width = 30  # Not in Degree

        cb_group = ReentrantCallbackGroup()

        # 2. Subscribers
        self.subscribe_bridge_node = self.create_subscription(
            SystemRequest,
            '/bridge_node/system_request',
            self.bridge_node_callback,
<<<<<<< HEAD
<<<<<<< HEAD
            10)  
=======
            10)
>>>>>>> 1f574e34b3dd02bb140180baa723fae6e2293a4d
=======
            10
        )
>>>>>>> a406b8482c402fe3f828bf13b92fc6d203dc7ea9

        # 3. Publishers
        self.publish_operational_mode = self.create_publisher(
            OperationalMode,
            '/operational_mode/current',
            10
        )

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
<<<<<<< HEAD
        self.check_system_timer = self.create_timer(
            10.0, self.check_system_status
=======
        self.get_logger().info(
            "command_node bereit -- Steuerung ausschliesslich ueber "
            "/bridge_node/system_request (SET_STATE / REBOOT / SHUTDOWN)."
>>>>>>> 1f574e34b3dd02bb140180baa723fae6e2293a4d
=======
        self.check_system_timer = self.create_timer(
            10.0, self.check_system_status)

        # 5. Services (Clients)
        self.clear_wedge_session_client = self.create_client(
            Trigger, "clear_wedge_session", callback_group=cb_group,
        )
        self.save_wedge_points_client = self.create_client(
            Trigger, "save_wedge_points", callback_group=cb_group,
        )
        self.finalize_ground_segmentation_client = self.create_client(
            Trigger, "finalize_ground_segmentation", callback_group=cb_group,
        )
        self.combine_wedges_client = self.create_client(
            Trigger, "combine_wedges", callback_group=cb_group,
        )

        self.get_logger().info(
            "command_node bereit -- Steuerung ausschliesslich ueber "
            "/bridge_node/system_request (SET_STATE / REBOOT / SHUTDOWN)."
>>>>>>> a406b8482c402fe3f828bf13b92fc6d203dc7ea9
        )

    # ------------------------------------------------------------------
    # Generischer Helper fuer alle vier Trigger-Services -- blockiert
    # den aufrufenden Thread, bis die Antwort da ist oder ein Timeout
    # greift. Braucht die ReentrantCallbackGroup + MultiThreadedExecutor
    # (siehe main()), sonst deadlockt es.
    # ------------------------------------------------------------------
    def _call_trigger(self, client, name, timeout_sec=10.0):
        if not client.wait_for_service(timeout_sec=timeout_sec):
            self.get_logger().error(f"{name}: Service nicht verfuegbar.")
            return False, f"{name} nicht verfuegbar"

        future = client.call_async(Trigger.Request())

        wait_start = time.time()
        while not future.done():
            if time.time() - wait_start > timeout_sec:
                self.get_logger().error(f"{name}: Timeout.")
                return False, f"{name} Timeout"
            time.sleep(0.05)

        result = future.result()
        self.get_logger().info(
            f"{name}: success={result.success}, message={result.message}"
        )
        return result.success, result.message

    # triggert by stm message
    def bridge_node_callback(self, msg):

        if msg.task == "SET_STATE":
            msg_state = OperationalMode()
            msg_state.mode = msg.message  # Ergebnis: "STANDBY"

            msg_log = LogMessage()
            msg_log.source = "JETSON"
            msg_log.event = "INFO"
            msg_log.details = f"Changing mode to from {self.state} to {msg.message}"

            self.old_state = self.state
            self.state = msg.message  # Update the internal state
            self.publish_operational_mode.publish(msg_state)
            self.publish_operational_log.publish(msg_log)

            self.check_state()



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

    # triggert by timer
    def trigger_housekeeping(self):

        msg = LogMessage()
        msg.source = "JETSON"
        msg.event = "INFO"
        msg.details = "Request to aquire house keeping data."

        self.publish_operational_log.publish(msg)
        self.publish_trigger_hkd.publish(String(data="trigger"))

    # triggert by timer
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

    # triggert by timer
    def check_system_status(self):
        i = 1

    def check_state(self):

        valid_states = ["STANDBY", "MAPPING", "SAFE", "ASSEMBLY_MAP", "TRACKING", "HOT_SWAP", "MAST_DEPLOYMENT"]

        if self.state not in valid_states:
            self.get_logger().error(f"Invalid state: {self.state}")
            return False
    # Neu: Uebergang in MAPPING startet die Wedge-Session
        elif self.state == "MAPPING" and self.old_state != "MAPPING":
            self._start_mapping()
    
        # Wenn wir MAPPING verlassen, laueft der Mapping-Timer nicht weiter
        elif self.old_state == "MAPPING" and self.state != "MAPPING":
            self._stop_mapping()

        elif self.state == "TRACKING":
            placeholder = 1  # Hier können Sie die Logik für den TRACKING-Zustand implementieren

        elif self.state == "HOT_SWAP":
            try:
                self.publish_operational_log.publish(LogMessage(source="JETSON", event="INFO", details="Shutting down system..."))
                subprocess.Popen(['systemctl', 'poweroff'])
            except Exception as e:
                self.publish_operational_log.publish(LogMessage(source="JETSON", event="ERROR", details=f"Shutdown failed: {e}"))

        elif self.state == "MAST_DEPLOYMENT":
            placeholder = 1  # Hier können Sie die Logik für den MAST_DEPLOYMENT-Zustand implementieren


        

            
    # ------------------------------------------------------------------
    # Wird einmalig beim Uebergang in MAPPING aufgerufen (aus
    # bridge_node_callback).
    # ------------------------------------------------------------------
    def _start_mapping(self):
        # trigger srv clear if self.wedges == 0
        if self.wedges == 0:
            self._call_trigger(
                self.clear_wedge_session_client, "clear_wedge_session"
            )

        # start timer (nach 3 min soll getriggert werden)
        if self.mapping_timer is None:
            self.mapping_timer = self.create_timer(180.0, self.timer_mapping)

        self.get_logger().info(
            f"Mapping gestartet. wedges={self.wedges}/{self.max_wedges}."
        )

    def _stop_mapping(self):
        if self.mapping_timer is not None:
            self.mapping_timer.destroy()
            self.mapping_timer = None
        self.get_logger().info("Mapping-Timer gestoppt (state != MAPPING).")

    # triggert alle 3 Minuten, solange state == MAPPING
    def timer_mapping(self):

        msg = LogMessage()
        msg.source = "JETSON"
        msg.event = "INFO"
        msg.details = "Mapping timer triggered. Requesting to save current map slice."
        self.publish_operational_log.publish(msg)

        # 1. aktuelle Wedge fertig klassifizieren + publishen lassen
        self._call_trigger(
            self.finalize_ground_segmentation_client, "finalize_ground_segmentation"
        )

        # 2. Mast-Rotation ansteuern, damit der naechste Wedge-Bereich
        #    gescannt werden kann. Kein eigener Service dafuer vorhanden --
        #    ueber den bestehenden SystemRequest-Publisher geschickt.
        #    ANPASSEN: Task-Name je nachdem, wie der Mast-Node es erwartet.
        mast_msg = SystemRequest()
        mast_msg.source = "JETSON"
        mast_msg.task = "ROTATE_MAST"
        mast_msg.message = str(self.wedge_width)
        self.publish_system_request.publish(mast_msg)

        # 3. aktuellen Wedge-Ausschnitt als Rohdaten sichern
        self._call_trigger(
            self.save_wedge_points_client, "save_wedge_points"
        )

        self.wedges += 1

        self.get_logger().info(
            f"timer_mapping: wedge {self.wedges}/{self.max_wedges} gesichert."
        )

        # wedges genug?
        if self.wedges >= self.max_wedges:
            # trigger das map in wedges combine ausgegeben wird
            self._call_trigger(
                self.combine_wedges_client, "combine_wedges", timeout_sec=30.0
            )

            # setze wedges auf 0
            self.wedges = 0

            self.get_logger().info(
                "timer_mapping: max_wedges erreicht, combine_wedges ausgeloest, "
                "wedges zurueckgesetzt."
            )


def main(args=None):
    rclpy.init(args=args)
    node = CommandNode()

    # 2 Threads minimum -- timer_mapping/_call_trigger blockieren auf
    # eingehende Service-Antworten, waehrend der Node parallel noch auf
    # /bridge_node/system_request, Timer usw. reagieren koennen muss.
    executor = MultiThreadedExecutor(num_threads=2)
    executor.add_node(node)

    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()