import math
import subprocess
import time


import rclpy
from rclpy.node import Node
from rclpy.callback_groups import ReentrantCallbackGroup, MutuallyExclusiveCallbackGroup
from rclpy.executors import MultiThreadedExecutor

# Uniform Service Interface
from rover_control_msgs.msg import OperationalMode, SystemRequest, LogMessage
from std_msgs.msg import String, Float64
from std_srvs.srv import Trigger


class CommandNode(Node):
    def __init__(self):
        super().__init__('command_node')

        # 1. Variablen
        self.state = "STANDBY"  # Initialer Modus
        self.old_state = "STANDBY"  # Initialer alter Modus
        self.wedges = 0
        self.max_wedges = 2         # Anzahl Wedges pro Mapping-Session -- anpassen
        self.mapping_timer = None    # nur aktiv, solange eine Mapping-Session laeuft
        self.wedges_width = 30  # Not in Degree
        self.time_mapping = 60 # time for mapping in sec
        self.neutral_position = 0.0 #355.5/(180.0*math.pi)  # Neutral position in rad
        self.neutral_wait_s = 5.0

        # Karten-Abschluss
        self.combine_settle_s = 2.0   # Wartezeit nach MAP_COMBINE, bis die Auswerte-Nodes ON sind
        self.save_settle_s = 2.0      # Wartezeit nach combine, bis obstacle_grid gerechnet hat
        self.max_wedge_retries = 2    # Fehlversuche je Mast-Position, bevor sie uebersprungen wird
        self.wedge_retries = 0

        self.motor5_position_old = 0.0
        self.motor5_position_new = 0.0

        cb_group = ReentrantCallbackGroup()
        # eigene Gruppe fuer STM-/WiFi-Befehle und ALIVE -- so laufen sie
        # weiter, auch waehrend timer_mapping auf Service-Antworten wartet
        cmd_group = MutuallyExclusiveCallbackGroup()

        # 2. Subscribers
        self.subscribe_bridge_node = self.create_subscription(
            SystemRequest,
            '/bridge_node/system_request',
            self.bridge_node_callback,
            10,
            callback_group=cmd_group,)

        self.subscribe_xm430_node = self.create_subscription(
            Float64,
            '/xm430_node/current_position',
            self.motor_rotation_callback,
            10
        )

        self.subscribe_wifi_node = self.create_subscription(
            SystemRequest,
            '/wifi_node/system_request',
            self.bridge_node_callback,   # gleicher Callback
            10,
            callback_group=cmd_group,
        )

        # 3. Publishers
        self.publish_rotation_position = self.create_publisher(
            Float64,
            '/xm430_node/goal_position',
            10
        )
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
            5.0, self.send_alive_message, callback_group=cmd_group
        )

        self.get_logger().info(
            "command_node bereit -- Steuerung ausschliesslich ueber "
            "/bridge_node/system_request (SET_STATE / REBOOT / SHUTDOWN)."
        )

        #self.check_system_timer = self.create_timer(
        #    10.0, self.check_system_status)

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
        # fertige Karte speichern (obstacle_grid_node)
        self.save_terrain_map_client = self.create_client(
            Trigger, "save_terrain_map", callback_group=cb_group,
        )


    # blockiert den aufrufenden Thread, bis die Antwort da ist oder ein Timeout
    # greift. Braucht die ReentrantCallbackGroup + MultiThreadedExecutor

    def motor_rotation_callback(self, msg):
        self.motor5_position_old = msg.data

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

    def _log_op(self, message, event="INFO"):
        self.publish_operational_log.publish(LogMessage(
            source="JETSON", event=event, message=message))

    def _set_mode(self, mode):
        """Internen Zustand setzen und an set_mode_node weitergeben."""
        self.state = mode
        self.publish_operational_mode.publish(OperationalMode(mode=mode))

    # triggert by stm message
    def bridge_node_callback(self, msg):

        if msg.task == "SET_STATE" and msg.message in ("RETRACT", "SHUTDOWN"):
            self._stop_mapping()
            self.wedges = 0
            self.old_state = self.state
            self.state = "STANDBY"
            self.publish_operational_mode.publish(OperationalMode(mode="STANDBY"))
            self._mast_to_neutral()
            if msg.message == "SHUTDOWN":
                self._run_later(self.neutral_wait_s, self._poweroff)
            return

        if msg.task == "SET_STATE":
            msg_state = OperationalMode()
            msg_state.mode = msg.message  # Ergebnis: "STANDBY"

            msg_log = LogMessage()
            msg_log.source = "JETSON"
            msg_log.event = "INFO"
            msg_log.message = f"Changing mode to from {self.state} to {msg.message}"

            self.old_state = self.state
            self.state = msg.message  # Update the internal state
            self.publish_operational_mode.publish(msg_state)
            self.publish_operational_log.publish(msg_log)

            self.check_state()



        if msg.task == "REBOOT":
            self._mast_to_neutral()
            self._run_later(self.neutral_wait_s, self._reboot)

        if msg.task == "SHUTDOWN":
            self._mast_to_neutral()
            self._run_later(self.neutral_wait_s, self._poweroff)

    def _mast_to_neutral(self):
        self.publish_rotation_position.publish(Float64(data=self.neutral_position))
        self.publish_operational_log.publish(LogMessage(
            source="JETSON", event="INFO",
            message="Mast (motor 5) moving to neutral position."))

    def _run_later(self, delay_s, fn):
        holder = {}

        def _cb():
            holder["t"].cancel()
            self.destroy_timer(holder["t"])
            fn()

        holder["t"] = self.create_timer(delay_s, _cb)

    def _poweroff(self):
        try:
            self.publish_operational_log.publish(LogMessage(
                source="JETSON", event="INFO", message="Shutting down system..."))
            subprocess.Popen(['systemctl', 'poweroff'])
        except Exception as e:
            self.publish_operational_log.publish(LogMessage(
                source="JETSON", event="ERROR", message=f"Shutdown failed: {e}"))

    def _reboot(self):
        try:
            self.publish_operational_log.publish(LogMessage(
                source="JETSON", event="INFO", message="Rebooting system..."))
            subprocess.run(['systemctl', 'reboot'], check=True)
        except subprocess.CalledProcessError as e:
            self.publish_operational_log.publish(LogMessage(
                source="JETSON", event="ERROR", message=f"Reboot failed: {e}"))

    # triggert by timer
    def trigger_housekeeping(self):

        msg = LogMessage()
        msg.source = "JETSON"
        msg.event = "INFO"
        msg.message = "Request to aquire house keeping data."

        self.publish_operational_log.publish(msg)
        self.publish_trigger_hkd.publish(String(data="trigger"))

    # triggert by timer
    def send_alive_message(self):

        msg_log = LogMessage()
        msg_log.source = "JETSON"
        msg_log.event = "INFO"
        msg_log.message = "System is alive and operational."

        msg_system = SystemRequest()
        msg_system.source = "JETSON"
        msg_system.task = "ALIVE"
        msg_system.message = self.state

        self.publish_operational_log.publish(msg_log)
        self.publish_system_request.publish(msg_system)
        self.publish_wifi.publish(String(data="get_status"))

    # triggert by timer

    def check_state(self):

        valid_states = ["STANDBY", "MAPPING", "SAFE", "ASSEMBLY_MAP", "MAP_COMBINE",
                        "TRACKING", "HOT_SWAP", "MAST_DEPLOYMENT"]

        if self.state not in valid_states:
            self.get_logger().error(f"Invalid state: {self.state}")
            return False

        # Mapping von aussen abgebrochen (anderer Zustand per STM/GUI,
        # waehrend eine Session laeuft) -> Timer stoppen UND Session
        # zuruecksetzen, damit das naechste MAPPING sauber bei Wedge 0 beginnt.
        # Eigenes 'if' (nicht Teil der elif-Kette), damit z.B. HOT_SWAP
        # danach trotzdem ausgefuehrt wird.
        if self.state != "MAPPING" and self.mapping_timer is not None:
            self._stop_mapping()
            self.wedges = 0
            self._log_op(f"Mapping aborted (new state {self.state}) -- session reset, nothing saved.",
                         event="ERROR")

        #Uebergang in MAPPING startet die Wedge-Session
        if self.state == "MAPPING" and self.old_state != "MAPPING":
            self._start_mapping()

        elif self.state == "TRACKING":
            placeholder = 1

        elif self.state == "HOT_SWAP":
            self._mast_to_neutral()
            self._run_later(self.neutral_wait_s, self._poweroff)


        elif self.state == "MAST_DEPLOYMENT":
            placeholder = 1


    # Wird einmalig beim Uebergang in MAPPING aufgerufen (ausbridge_node_callback).

    def _start_mapping(self):
        # trigger srv clear if self.wedges == 0
        if self.wedges == 0:
            self._call_trigger(
                self.clear_wedge_session_client, "clear_wedge_session"
            )
            self.motor5_position_old = - math.pi
            self.publish_rotation_position.publish(Float64(data=self.motor5_position_old))
            self.wedge_retries = 0

        # start timer (nach time_mapping soll getriggert werden)
        if self.mapping_timer is None:
            self.mapping_timer = self.create_timer(self.time_mapping, self.timer_mapping)

        self.get_logger().info(
            f"Mapping gestartet. wedges={self.wedges}/{self.max_wedges}."
        )

    def _stop_mapping(self):
        if self.mapping_timer is not None:
            self.mapping_timer.cancel()
            self.destroy_timer(self.mapping_timer)
            self.mapping_timer = None
        self.get_logger().info("Mapping-Timer gestoppt.")

    # triggert alle time_mapping Sekunden, solange eine Session laeuft
    def timer_mapping(self):
        if self.mapping_timer is None:
            return  # Session wurde inzwischen abgebrochen

        self._log_op("Mapping timer triggered. Saving current wedge.")

        # 1. Wedge sichern, SOLANGE die Perception noch ON ist
        #    Das finalize pro Wedge entfaellt: klassifiziert wird erst am
        #    Ende ueber die kombinierte Wolke.
        ok, msg = self._call_trigger(self.save_wedge_points_client, "save_wedge_points")

        if self.mapping_timer is None:
            return  # waehrend des Speicherns abgebrochen

        if ok:
            self.wedges += 1
            self.wedge_retries = 0
            self._log_op(f"Wedge {self.wedges}/{self.max_wedges} saved.")
            self.get_logger().info(f"timer_mapping: wedge {self.wedges}/{self.max_wedges} gesichert.")
        else:
            self.wedge_retries += 1
            if self.wedge_retries <= self.max_wedge_retries:
                # gleiche Mast-Position, naechster Timer-Durchlauf versucht es erneut
                self._log_op(f"Saving wedge failed ({msg}) -- retry "
                             f"{self.wedge_retries}/{self.max_wedge_retries} at same position.",
                             event="ERROR")
                return
            # zu oft gescheitert -> Position ueberspringen, damit die Session endet
            self.wedges += 1
            self.wedge_retries = 0
            self._log_op(f"Wedge {self.wedges}/{self.max_wedges} skipped after repeated failures ({msg}).",
                         event="ERROR")

        if self.wedges >= self.max_wedges:
            self._finish_mapping()
            return

        # 2. Perception aus, Mast zur naechsten Position drehen
        self._set_mode("ASSEMBLY_MAP")
        self._log_op("Perception off, rotating mast for next wedge.")

        if self.motor5_position_old <= math.pi:
            self.motor5_position_new = self.motor5_position_old + 2 * math.pi /(self.max_wedges)
            self.publish_rotation_position.publish(Float64(data=self.motor5_position_new))
            self.motor5_position_old = self.motor5_position_new
            self._log_op(f"Rotating mast to position {self.motor5_position_new} rad for next wedge.")
        time.sleep(2.0)  # give time for mast to move

        if self.mapping_timer is None:
            return  # waehrend der Drehung abgebrochen -> nicht wieder einschalten

        # 3. naechster Wedge: Perception wieder an (leert den Puffer von
        #    ground_segmentation_node) und dem Wedge die volle Scanzeit geben
        self._set_mode("MAPPING")
        self.mapping_timer.reset()

    # Abschluss der Session -- Wedges kombinieren, Karte speichern
    def _finish_mapping(self):
        self._stop_mapping()
        self._log_op("All wedges saved -- combining map.")

        # 1. Nur die Auswerte-Pipeline an (Sensoren aus): ground_segmentation_
        #    und obstacle_grid_node gehen ON, ground_segmentation startet mit
        #    leerem Puffer, es kommen keine Live-Daten dazu.
        self._set_mode("ASSEMBLY_MAP")   # erst alles OFF -> sauberer Neustart der Auswerte-Nodes
        time.sleep(1.5)
        self._set_mode("MAP_COMBINE")
        time.sleep(self.combine_settle_s)

        # 2. Wedges laden, zusammenfuegen, klassifizieren
        #    (combine_wedges ruft finalize_ground_segmentation selbst auf).
        ok_c, msg_c = self._call_trigger(
            self.combine_wedges_client, "combine_wedges", timeout_sec=30.0
        )

        ok_s, msg_s = False, "not attempted (combine failed)"
        if ok_c:
            # obstacle_grid_node braucht kurz, um ground_points zu gridden
            time.sleep(self.save_settle_s)
            # 3. fertige Karte nach terrain_map.npz schreiben
            ok_s, msg_s = self._call_trigger(
                self.save_terrain_map_client, "save_terrain_map", timeout_sec=10.0
            )

        if ok_c and ok_s:
            self._log_op(f"Mapping completed, map saved: {msg_s}")
        else:
            self._log_op(f"Mapping finished WITHOUT saved map. combine: {msg_c} | save: {msg_s}",
                         event="ERROR")

        # 4. Session beenden
        self.wedges = 0
        self.old_state = "MAPPING"
        self._set_mode("STANDBY")
        self._mast_to_neutral()
        self.get_logger().info("Mapping-Session beendet, zurueck in STANDBY.")


def main(args=None):
    rclpy.init(args=args)
    node = CommandNode()

    # 3 Threads -- timer_mapping blockiert auf Service-Antworten
    # (Reentrant-Gruppe braucht einen Thread fuer die Antworten), und
    # STM-/WiFi-Befehle + ALIVE (cmd_group) sollen parallel weiterlaufen.
    executor = MultiThreadedExecutor(num_threads=3)
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