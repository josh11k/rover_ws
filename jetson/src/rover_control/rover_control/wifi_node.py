import rclpy
import os
import shutil
import signal
import subprocess
import threading

try:
    from flask import Flask, jsonify, request
except ImportError:  # pip install flask
    Flask = None

from rclpy.node import Node
from std_msgs.msg import String

from rover_control_msgs.msg import LogMessage, OperationalMode, SystemRequest


PAGE = """<!doctype html>
<html><head><meta charset="utf-8"><title>Rover</title>
<style>body{font-family:sans-serif;margin:20px}button{margin:3px;padding:8px}
#out{background:#eee;padding:8px;margin-top:10px;white-space:pre-wrap}
img{max-width:100%;margin-top:10px;display:none}</style></head><body>
<h2>Rover</h2>
<div>Zustand: <b id="state">?</b> | Kamera: <b id="cam">?</b></div>
<div>
 <button onclick="send('get_status')">get_status</button>
 <button onclick="send('get_map')">get_map</button>
 <button onclick="send('get_hkd')">get_hkd</button>
</div>
<div>
 <button onclick="send('set_state STANDBY')">STANDBY</button>
 <button onclick="send('set_state MAPPING')">MAPPING</button>
 <button onclick="send('set_state SAFE')">SAFE</button>
</div>
<div>
 <button onclick="send('camera_on')">Kamera an</button>
 <button onclick="send('camera_off')">Kamera aus</button>
</div>
<div><input id="free" size="30" placeholder="beliebiger Befehl">
 <button onclick="send(document.getElementById('free').value)">senden</button></div>
<div id="out"></div>
<img id="cam_img">
<script>
async function send(c){
  const r = await fetch('/cmd',{method:'POST',body:c});
  document.getElementById('out').textContent = JSON.stringify(await r.json());
  if(c==='camera_on') setTimeout(showCam,2500);
  if(c==='camera_off') hideCam();
}
function showCam(){
  const i=document.getElementById('cam_img');
  i.src='http://'+location.hostname+':__CAM_PORT__/stream?topic=__CAM_TOPIC__&type=mjpeg&quality=50';
  i.style.display='block';
}
function hideCam(){const i=document.getElementById('cam_img');i.src='';i.style.display='none';}
async function poll(){
  try{const j=await (await fetch('/status')).json();
    document.getElementById('state').textContent=j.state;
    document.getElementById('cam').textContent=j.camera?'an':'aus';}catch(e){}
}
setInterval(poll,2000);poll();
</script></body></html>"""


class WifiNode(Node):

    def __init__(self):
        super().__init__("wifi_node")

        self.declare_parameter("map_path", "/home/team/rover_maps/terrain_map.npz")
        self.declare_parameter("hkd_path", "~/rover_log/")
        self.declare_parameter("web_port", 8080)
        self.declare_parameter("camera_port", 8081)
        self.declare_parameter("camera_topic", "/mono_cam/image_raw")

        self.source_path_map = os.path.expanduser(self.get_parameter("map_path").value)
        self.source_path_hkd = os.path.expanduser(self.get_parameter("hkd_path").value)
        self.web_port = int(self.get_parameter("web_port").value)
        self.camera_port = int(self.get_parameter("camera_port").value)
        self.camera_topic = self.get_parameter("camera_topic").value
        self.camera_proc = None
        self.target_user = "user"  # Ersetzen Sie dies durch den tatsächlichen

        self.target_ip = "192.168.2.61"

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
  
        self.publish_operational_log = self.create_publisher(
            LogMessage,
            '/log/operations',
            10
            )

        self.publish_system_request = self.create_publisher(
            SystemRequest,
            '/wifi_node/system_request',
            10
        )
    
    
        self._start_web_server()

    def state_callback(self, msg):
        self.state = msg.mode
    
    
    # ---------------- Kamera (web_video_server, per Befehl) ----------------
    def camera_running(self):
        return self.camera_proc is not None and self.camera_proc.poll() is None

    def start_camera(self):
        if self.camera_running():
            return "Kamera-Stream laeuft bereits"
        if shutil.which("ros2") is None:
            return "ros2 nicht gefunden"
        try:
            self.camera_proc = subprocess.Popen(
                ["ros2", "run", "web_video_server", "web_video_server",
                 "--ros-args", "-p", f"port:={self.camera_port}"],
                start_new_session=True,
            )
        except OSError as e:
            return f"Kamera-Stream konnte nicht starten: {e}"
        return f"Kamera-Stream gestartet auf Port {self.camera_port}"

    def stop_camera(self):
        if not self.camera_running():
            return "Kamera-Stream war nicht aktiv"
        try:
            os.killpg(os.getpgid(self.camera_proc.pid), signal.SIGINT)
            self.camera_proc.wait(timeout=3)
        except Exception:
            try:
                os.killpg(os.getpgid(self.camera_proc.pid), signal.SIGKILL)
            except Exception:
                pass
        self.camera_proc = None
        return "Kamera-Stream gestoppt"

    # ---------------- Webserver (Flask) ----------------
    def _start_web_server(self):
        if Flask is None:
            self.get_logger().error("Flask fehlt: pip install flask - Webserver nicht gestartet")
            return

        app = Flask(__name__)
        node = self

        @app.route("/")
        def index():
            return (PAGE.replace("__CAM_PORT__", str(node.camera_port))
                        .replace("__CAM_TOPIC__", node.camera_topic))

        @app.route("/status")
        def status():
            return jsonify(state=node.state, camera=node.camera_running())

        @app.route("/cmd", methods=["GET", "POST"])
        def cmd():
            text = (request.values.get("c") or request.get_data(as_text=True) or "").strip()
            if not text:
                return jsonify(ok=False, error="leerer Befehl"), 400
            node.incoming_callback(String(data=text))
            return jsonify(ok=True, cmd=text, camera=node.camera_running())

        threading.Thread(
            target=lambda: app.run(host="0.0.0.0", port=node.web_port,
                                   threaded=True, use_reloader=False),
            daemon=True,
        ).start()
        self.get_logger().info(f"Webserver auf Port {node.web_port}")
    

    def incoming_callback(self, msg):
        if msg.data == "get_map":
            msg_log = LogMessage()
            msg_log.source = "CONTROLLER"
            msg_log.event = "REQUEST"
            msg_log.message = "Map requested via WiFi"
            self.publish_wifi_log.publish(msg_log)
            self.publish_operational_log.publish(msg_log)
            
            success, message = send_map_via_rsync(
                self.source_path_map,
                self.target_user,
                self.target_ip,
                self.target_dir,
            )

            if success == True:
                self.publish_operational_log.publish(LogMessage(source="JETSON", event="MAP_TRANSFER_SUCCESS", message=message))
                self.publish_wifi_log.publish(LogMessage(source="JETSON", event="MAP_TRANSFER_SUCCESS", message=message))
            else:
                self.publish_operational_log.publish(LogMessage(source="JETSON", event="MAP_TRANSFER_FAILURE", message=message))
                self.publish_wifi_log.publish(LogMessage(source="JETSON", event="MAP_TRANSFER_FAILURE", message=message))   

        if msg.data == "get_hkd": #housekeepingdata
            msg_log = LogMessage()
            msg_log.source = "CONTROLLER"
            msg_log.event = "REQUEST"
            msg_log.message = "Housekeeping Data requested via WiFi"
            self.publish_wifi_log.publish(msg_log)
            self.publish_operational_log.publish(msg_log)

            success, message = send_csv_via_rsync(
                self.source_path_hkd,
                self.target_user,
                self.target_ip,
                self.target_dir,
            )

            if success == True:
                self.publish_operational_log.publish(LogMessage(source="JETSON", event="HKD_TRANSFER_SUCCESS", message=message))
                self.publish_wifi_log.publish(LogMessage(source="JETSON", event="HKD_TRANSFER_SUCCESS", message=message))
            else:
                self.publish_operational_log.publish(LogMessage(source="JETSON", event="HKD_TRANSFER_FAILURE", message=message))
                self.publish_wifi_log.publish(LogMessage(source="JETSON", event="HKD_TRANSFER_FAILURE", message=message))

        if msg.data == "get_status":
            msg_log = LogMessage()
            msg_log.source = "CONTROLLER"
            msg_log.event = "REQUEST"
            msg_log.message = "Status requested via WiFi"
            self.publish_wifi_log.publish(msg_log)
            self.publish_operational_log.publish(msg_log)

            # Hier können Sie den Status des Jetson-Boards abrufen und zurücksenden
            status_message = f"Jetson is operational. State: {self.state} "
            self.pub_wifi.publish(String(data=status_message))

        elif msg.data.startswith("set_state"):
            # erlaubt "set_state MAPPING", "set_state:MAPPING", "set_state=MAPPING"
            new_state = msg.data[len("set_state"):].strip(" :=").upper()

            if not new_state:
                self.publish_wifi_log.publish(LogMessage(
                    source="CONTROLLER", event="ERROR",
                    message=f"set_state ohne Zielzustand: '{msg.data}'"))
                return

            msg_log = LogMessage()
            msg_log.source = "CONTROLLER"
            msg_log.event = "REQUEST"
            msg_log.message = f"State change to {new_state} requested via WiFi"
            self.publish_wifi_log.publish(msg_log)
            self.publish_operational_log.publish(msg_log)

            msg_system = SystemRequest()
            msg_system.source = "WIFI"
            msg_system.task = "SET_STATE"
            msg_system.message = new_state
            self.publish_system_request.publish(msg_system)

        elif msg.data == "camera_on":
            self.publish_wifi_log.publish(LogMessage(
                source="CONTROLLER", event="REQUEST", message=self.start_camera()))

        elif msg.data == "camera_off":
            self.publish_wifi_log.publish(LogMessage(
                source="CONTROLLER", event="REQUEST", message=self.stop_camera()))

        



        
  



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

    try:
        rclpy.spin(node)
    finally:
        node.stop_camera()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()