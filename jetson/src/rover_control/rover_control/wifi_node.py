import rclpy
import os
import shutil
import subprocess

from rclpy.node import Node
from std_msgs.msg import String

from rover_control_msgs.msg import LogMessage, OperationalMode


class WifiNode(Node):

    def __init__(self):
        super().__init__("wifi_node")

        self.source_path_map = "~/map"
        self.source_path_hkd = "~/rover_log"
        self.target_user = "user"  # Ersetzen Sie dies durch den tatsächlichen
        self.target_ip = "192.168.1.100"
        self.target_dir = "~/rover_data/"

        self.state = "STANDBY"  # Initialer Zustand

        # 2. Subscriber für eingehende Nachrichten
        self.sub_wifi = self.create_subscription(
            String,
            "/wifi/incoming_message",
            self.incoming_callback,
            10
        )

        self.sub_wifi_trigger = self.create_subscription(
            String,
            "/trigger/wifi",
            self.incoming_callback,
            10
        )

        self.sub_state = self.create_subscription(
            OperationalMode,
            "operational_mode/current",
            self.state_callback,
            10
        )


        # 3. Publisher für ausgehende Nachrichten
        self.pub_wifi = self.create_publisher(
            String,
            "/wifi/outgoing_message",
            10
        )

        self.publish_wifi_log = self.create_publisher(
            LogMessage, 
            '/log/wifi',
            10
            )        
  
        self.publish_operational_mode = self.create_publisher(
            LogMessage,
            '/log/operations',
            10
            )

    def state_callback(self, msg):
        self.state = msg.mode
    

    def incoming_callback(self, msg):
        if msg.data == "get_map":
            msg_log = LogMessage()
            msg_log.source = "CONTROLLER"
            msg_log.event = "REQUEST"
            msg_log.details = "Map requested via WiFi"
            self.publish_wifi_log.publish(msg_log)
            self.publish_operational_mode.publish(msg_log)
            
            success, message = send_map_via_rsync(
                self.source_path_map,
                self.target_user,
                self.target_ip
            )

            if success == True:
                self.publish_operational_mode.publish(LogMessage(source="JETSON", event="MAP_TRANSFER_SUCCESS", details=message))
                self.publish_wifi_log.publish(LogMessage(source="JETSON", event="MAP_TRANSFER_SUCCESS", details=message))
            else:
                self.publish_operational_mode.publish(LogMessage(source="JETSON", event="MAP_TRANSFER_FAILURE", details=message))
                self.publish_wifi_log.publish(LogMessage(source="JETSON", event="MAP_TRANSFER_FAILURE", details=message))   

        if msg.data == "get_hkd": #housekeepingdata
            msg_log = LogMessage()
            msg_log.source = "CONTROLLER"
            msg_log.event = "REQUEST"
            msg_log.details = "Housekeeping Data requested via WiFi"
            self.publish_wifi_log.publish(msg_log)
            self.publish_operational_mode.publish(msg_log)

            success, message = send_csv_via_rsync(
                self.source_path_hkd,
                self.target_user,
                self.target_ip,
            )

            if success == True:
                self.publish_operational_mode.publish(LogMessage(source="JETSON", event="HKD_TRANSFER_SUCCESS", details=message))
                self.publish_wifi_log.publish(LogMessage(source="JETSON", event="HKD_TRANSFER_SUCCESS", details=message))
            else:
                self.publish_operational_mode.publish(LogMessage(source="JETSON", event="HKD_TRANSFER_FAILURE", details=message))
                self.publish_wifi_log.publish(LogMessage(source="JETSON", event="HKD_TRANSFER_FAILURE", details=message))

        if msg.data == "get_status":
            msg_log = LogMessage()
            msg_log.source = "CONTROLLER"
            msg_log.event = "REQUEST"
            msg_log.details = "Status requested via WiFi"
            self.publish_wifi_log.publish(msg_log)
            self.publish_operational_mode.publish(msg_log)

            # Hier können Sie den Status des Jetson-Boards abrufen und zurücksenden
            status_message = f"Jetson is operational. State: {self.state} "
            self.pub_wifi.publish(String(data=status_message))

        
  



def send_map_via_rsync(
    source_path: str,
    target_user: str,
    target_ip: str,
    target_dir: str = "~/",
) -> tuple[bool, str]:
    """
    Überträgt eine Datei oder ein Verzeichnis per rsync an ein Zielgerät.

    Returns:
        (True, Erfolgsmeldung)
        (False, Fehlermeldung)
    """

    # 1. Prüfen, ob rsync installiert ist
    if shutil.which("rsync") is None:
        return False, "rsync ist auf dem Jetson nicht installiert."

    # 2. Prüfen, ob die Quelle existiert
    if not os.path.exists(source_path):
        return False, f"Quellpfad existiert nicht: {source_path}"

    # 3. rsync-Befehl aufbauen
    cmd = [
        "rsync",
        "-av",
        "--partial",
        source_path,
        f"{target_user}@{target_ip}:{target_dir}",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        return True, result.stdout.strip() or "Übertragung erfolgreich."

    except subprocess.CalledProcessError as e:
        error = e.stderr.strip()

        return (
            False,
            f"rsync Fehler (Code {e.returncode}): {error}",
        )

    except OSError as e:
        return False, f"Systemfehler beim Starten von rsync: {e}"

    except Exception as e:
        return False, f"Unerwarteter Fehler: {e}"




def send_csv_via_rsync(
    source_path: str, # directory on jetson
    target_user: str, # user of laptop
    target_ip: str, # wifi adress of who is tr
    target_dir: str = "~/", # diectory on laptop
) -> tuple[bool, str]: 
    """
    Überträgt eine Datei oder ein Verzeichnis per rsync an ein Zielgerät.

    Returns:
        (True, Erfolgsmeldung)
        (False, Fehlermeldung)
    """

    # 1. Prüfen, ob rsync installiert ist
    if shutil.which("rsync") is None:
        return False, "rsync ist auf dem Jetson nicht installiert."

    # 2. Prüfen, ob die Quelle existiert
    if not os.path.exists(source_path):
        return False, f"Quellpfad existiert nicht: {source_path}"

    # 3. rsync-Befehl aufbauen
    cmd = [
        "rsync",
        "-av",
        "--partial",
        "--append-verify",
        source_path,
        f"{target_user}@{target_ip}:{target_dir}",
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
        )

        return True, result.stdout.strip() or "Übertragung erfolgreich."

    except subprocess.CalledProcessError as e:
        error = e.stderr.strip()

        return (
            False,
            f"rsync Fehler (Code {e.returncode}): {error}",
        )

    except OSError as e:
        return False, f"Systemfehler beim Starten von rsync: {e}"

    except Exception as e:
        return False, f"Unerwarteter Fehler: {e}"



def main(args=None):
    rclpy.init(args=args)

    node = WifiNode()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == "__main__":
    main()