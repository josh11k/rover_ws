import io
import os
import re
import shutil
import signal
import subprocess
import threading
import time
import zipfile
from collections import deque
from datetime import datetime

import rclpy
from rclpy.node import Node
from std_msgs.msg import String

from rover_control_msgs.msg import LogMessage, OperationalMode, SystemRequest

try:
    from flask import Flask, jsonify, request, send_file, abort
except ImportError:  # pip install flask
    Flask = None

# Log-Ordner aus log.py uebernehmen (eine einzige Quelle der Wahrheit)
try:
    from rover_control.log import LOG_DIRECTORY
except Exception:
    LOG_DIRECTORY = "/home/team/jetson/logs"

# Zustaende, die ueber die GUI gesetzt werden duerfen.
# HOT_SWAP fehlt bewusst: der command_node faehrt dabei den Jetson herunter.
VALID_STATES = ["STANDBY", "MAPPING", "SAFE", "ASSEMBLY_MAP", "TRACKING", "MAST_DEPLOYMENT"]

PAGE = """<!doctype html>
<html lang="de"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Rover WiFi-Interface</title>
<style>
 body{font-family:system-ui,sans-serif;margin:0;background:#f3f4f6;color:#111}
 header{background:#1f2937;color:#fff;padding:12px 20px;display:flex;gap:24px;align-items:center;flex-wrap:wrap}
 header h1{font-size:18px;margin:0}
 .pill{padding:3px 10px;border-radius:12px;background:#374151;font-size:13px}
 .pill.on{background:#15803d}.pill.off{background:#b91c1c}
 main{display:grid;grid-template-columns:repeat(auto-fit,minmax(380px,1fr));gap:16px;padding:16px}
 section{background:#fff;border-radius:8px;padding:14px 16px;box-shadow:0 1px 3px #0002}
 h2{font-size:15px;margin:0 0 10px;color:#374151}
 button{padding:7px 12px;margin:3px 3px 3px 0;border:1px solid #9ca3af;background:#f9fafb;border-radius:6px;cursor:pointer}
 button:hover{background:#e5e7eb}
 button.primary{background:#2563eb;color:#fff;border-color:#2563eb}
 input[type=text]{padding:7px;width:55%;border:1px solid #9ca3af;border-radius:6px}
 #feedback{margin-top:10px;padding:9px;border-radius:6px;background:#e5e7eb;min-height:20px;white-space:pre-wrap}
 #feedback.ok{background:#dcfce7;color:#14532d}#feedback.err{background:#fee2e2;color:#7f1d1d}
 #feedback.pend{background:#fef9c3;color:#713f12}
 table{width:100%;border-collapse:collapse;font-size:13px}
 td,th{padding:4px 6px;border-bottom:1px solid #e5e7eb;text-align:left;vertical-align:top}
 .ok{color:#15803d}.err{color:#b91c1c}
 #cam_img{max-width:100%;margin-top:8px;display:none;border-radius:6px}
 a.dl{color:#2563eb;text-decoration:none}a.dl:hover{text-decoration:underline}
 .muted{color:#6b7280;font-size:12px}
</style></head><body>
<header>
 <h1>Rover WiFi-Interface</h1>
 <span>Zustand: <span class="pill" id="state">?</span></span>
 <span>Kamera: <span class="pill" id="cam">?</span></span>
 <span>Verbindung: <span class="pill" id="conn">?</span></span>
</header>
<main>
 <section>
  <h2>Befehle</h2>
  <div>
   <button onclick="sendCmd('get_status')">Status abfragen</button>
   <button onclick="sendCmd('get_map')">Karte pruefen</button>
   <button onclick="sendCmd('get_hkd')">Logs pruefen</button>
  </div>
  <div class="muted">Zustand setzen:</div>
  <div id="state_buttons"></div>
  <div style="margin-top:6px">
   <input type="text" id="free" placeholder="Befehl, z. B. set_state MAPPING"
          onkeydown="if(event.key==='Enter')sendFree()">
   <button class="primary" onclick="sendFree()">Senden</button>
  </div>
  <div id="feedback">Bereit.</div>
 </section>

 <section>
  <h2>Befehlsverlauf</h2>
  <table><thead><tr><th>Zeit</th><th>Befehl</th><th>Ergebnis</th></tr></thead>
  <tbody id="history"></tbody></table>
 </section>

 <section>
  <h2>Kamera</h2>
  <button onclick="sendCmd('camera_on')">Stream starten</button>
  <button onclick="sendCmd('camera_off')">Stream stoppen</button>
  <div class="muted" id="cam_info"></div>
  <img id="cam_img" alt="Kamerabild">
 </section>

 <section>
  <h2>Downloads</h2>
  <div><b>Karte</b>: <span id="map_info" class="muted"></span></div>
  <div style="margin:6px 0 12px" id="map_link"></div>
  <div><b>Log-Dateien</b> <a class="dl" href="/download/logs.zip">(alle als ZIP)</a></div>
  <table><thead><tr><th>Datei</th><th>Groesse</th><th>Geaendert</th></tr></thead>
  <tbody id="files"></tbody></table>
  <button onclick="loadFiles()" style="margin-top:8px">Liste aktualisieren</button>
 </section>
</main>

<script>
var STATES = __STATES__;
var camShown = false;

function el(id){return document.getElementById(id);}
function setFeedback(text, cls){var f=el('feedback');f.textContent=text;f.className=cls||'';}

function buildStateButtons(){
  var box=el('state_buttons');
  STATES.forEach(function(s){
    var b=document.createElement('button');
    b.textContent=s;
    b.onclick=function(){sendCmd('set_state '+s);};
    box.appendChild(b);
  });
}

async function sendCmd(c){
  setFeedback('Sende "'+c+'" ...','pend');
  try{
    var r=await fetch('/api/cmd',{method:'POST',headers:{'Content-Type':'application/json'},
                                  body:JSON.stringify({cmd:c})});
    var j=await r.json();
    setFeedback((j.ok?'OK: ':'FEHLER: ')+j.msg, j.ok?'ok':'err');
    if(c==='camera_off'){hideCam();}
    if(c==='camera_on' && j.ok){setTimeout(showCam,800);}
  }catch(e){
    setFeedback('FEHLER: keine Verbindung zum Jetson','err');
  }
  refresh();
}
function sendFree(){var v=el('free').value.trim();if(v){sendCmd(v);el('free').value='';}}

var camPort=8081, camTopic='';
function showCam(){
  var i=el('cam_img');
  i.onerror=function(){el('cam_info').textContent='Kein Bild empfangen - Topic/Kamera pruefen.';};
  i.src='http://'+location.hostname+':'+camPort+'/stream?topic='+encodeURIComponent(camTopic)+
        '&type=mjpeg&quality=50&_='+Date.now();
  i.style.display='block';camShown=true;
}
function hideCam(){var i=el('cam_img');i.src='';i.style.display='none';camShown=false;}

function fmtSize(n){
  if(n>1048576)return (n/1048576).toFixed(1)+' MB';
  if(n>1024)return (n/1024).toFixed(1)+' KB';
  return n+' B';
}

async function refresh(){
  try{
    var j=await (await fetch('/api/status')).json();
    el('state').textContent=j.state;
    var c=el('cam');c.textContent=j.camera?'an':'aus';c.className='pill '+(j.camera?'on':'off');
    var k=el('conn');k.textContent='ok';k.className='pill on';
    camPort=j.camera_port;camTopic=j.camera_topic;
    el('cam_info').textContent='Topic: '+j.camera_topic+
      (j.camera_topic_publishers>0?' (Bildquelle aktiv)':' (keine Bildquelle)');
    if(j.camera && !camShown){showCam();}
    if(!j.camera && camShown){hideCam();}
    var tb=el('history');tb.innerHTML='';
    j.history.slice().reverse().forEach(function(h){
      var tr=document.createElement('tr');
      [h.time,h.cmd,(h.ok?'OK - ':'FEHLER - ')+h.msg].forEach(function(t,idx){
        var td=document.createElement('td');td.textContent=t;
        if(idx===2)td.className=h.ok?'ok':'err';
        tr.appendChild(td);
      });
      tb.appendChild(tr);
    });
  }catch(e){
    var k=el('conn');k.textContent='getrennt';k.className='pill off';
  }
}

async function loadFiles(){
  try{
    var j=await (await fetch('/api/files')).json();
    var m=j.map;
    el('map_info').textContent=m.exists?(fmtSize(m.size)+', '+m.mtime):'noch nicht vorhanden';
    el('map_link').innerHTML=m.exists?'<a class="dl" href="/download/map">terrain_map.npz herunterladen</a>':'';
    var tb=el('files');tb.innerHTML='';
    j.logs.forEach(function(f){
      var tr=document.createElement('tr');
      var td=document.createElement('td');
      var a=document.createElement('a');a.className='dl';a.textContent=f.name;
      a.href='/download/log/'+encodeURIComponent(f.name);td.appendChild(a);tr.appendChild(td);
      [fmtSize(f.size),f.mtime].forEach(function(t){
        var d=document.createElement('td');d.textContent=t;tr.appendChild(d);
      });
      tb.appendChild(tr);
    });
    if(j.logs.length===0){var tr=document.createElement('tr');var d=document.createElement('td');
      d.colSpan=3;d.textContent='Keine Log-Dateien gefunden in '+j.log_dir;tr.appendChild(d);tb.appendChild(tr);}
  }catch(e){}
}

buildStateButtons();refresh();loadFiles();
setInterval(refresh,2000);setInterval(loadFiles,15000);
</script></body></html>"""


def _fmt_time(ts):
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")


class WifiNode(Node):

    def __init__(self):
        super().__init__("wifi_node")

        # ---------------- Parameter ----------------
        self.declare_parameter("map_path", "/home/team/rover_maps/terrain_map.npz")
        self.declare_parameter("log_dir", LOG_DIRECTORY)
        self.declare_parameter("web_port", 8080)
        self.declare_parameter("camera_port", 8081)
        self.declare_parameter("camera_topic", "/mono_cam/image_raw")
        self.declare_parameter("state_confirm_timeout", 3.0)

        self.map_path = os.path.expanduser(self.get_parameter("map_path").value)
        self.log_dir = os.path.expanduser(self.get_parameter("log_dir").value)
        self.web_port = int(self.get_parameter("web_port").value)
        self.camera_port = int(self.get_parameter("camera_port").value)
        self.camera_topic = self.get_parameter("camera_topic").value
        self.state_confirm_timeout = float(self.get_parameter("state_confirm_timeout").value)

        # ---------------- Zustand ----------------
        self.state = "STANDBY"
        self.camera_proc = None
        self.history = deque(maxlen=50)
        self.history_lock = threading.Lock()
        self.camera_lock = threading.Lock()

        # ---------------- Subscriber ----------------
        self.sub_wifi = self.create_subscription(
            String, "/wifi/incoming_message", self.incoming_callback, 10)
        self.sub_wifi_trigger = self.create_subscription(
            String, "/trigger/wifi", self.incoming_callback, 10)
        self.sub_state = self.create_subscription(
            OperationalMode, "operational_mode/current", self.state_callback, 10)

        # ---------------- Publisher ----------------
        self.pub_wifi = self.create_publisher(String, "/wifi/outgoing_message", 10)
        self.publish_wifi_log = self.create_publisher(LogMessage, "/log/wifi", 10)
        self.publish_operational_log = self.create_publisher(LogMessage, "/log/operations", 10)
        self.publish_system_request = self.create_publisher(
            SystemRequest, "/wifi_node/system_request", 10)

        self._start_web_server()

    # ------------------------------------------------------------------
    # ROS-Seite
    # ------------------------------------------------------------------
    def state_callback(self, msg):
        self.state = msg.mode

    def incoming_callback(self, msg):
        """Befehle ueber ROS-Topics (z. B. /trigger/wifi vom command_node)."""
        text = msg.data.strip()
        # get_status kommt alle paar Sekunden vom command_node -> nicht in den Verlauf
        self.run_command(text, wait=False, record=(text != "get_status"))

    def _log(self, event, message):
        msg_log = LogMessage()
        msg_log.source = "CONTROLLER"
        msg_log.event = event
        msg_log.message = message
        self.publish_wifi_log.publish(msg_log)
        self.publish_operational_log.publish(msg_log)

    # ------------------------------------------------------------------
    # Befehlsausfuehrung (liefert immer (ok, text))
    # ------------------------------------------------------------------
    def run_command(self, text, wait=False, record=True):
        text = (text or "").strip()
        try:
            ok, msg = self._execute(text, wait)
        except Exception as e:  # nie eine Exception an die GUI durchreichen
            ok, msg = False, f"Interner Fehler: {e}"

        if record and text:
            with self.history_lock:
                self.history.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "cmd": text, "ok": ok, "msg": msg,
                })
            self._log("REQUEST" if ok else "ERROR", f"{text}: {msg}")

        self.pub_wifi.publish(String(data=f"{'OK' if ok else 'ERR'}: {msg}"))
        return ok, msg

    def _execute(self, text, wait):
        if not text:
            return False, "Leerer Befehl"

        head = re.split(r"[ :=]", text, maxsplit=1)[0].lower()

        if head == "get_status":
            return True, (f"Zustand {self.state}; Kamera "
                          f"{'an' if self.camera_running() else 'aus'}")

        if head == "get_map":
            info = self.map_info()
            if not info["exists"]:
                return False, f"Keine Karte vorhanden ({self.map_path})"
            return True, (f"Karte vorhanden ({info['size']} Bytes, {info['mtime']}) "
                          f"- ueber Downloads laden")

        if head in ("get_hkd", "get_logs"):
            logs = self.list_logs()
            if not logs:
                return False, f"Keine Log-Dateien in {self.log_dir}"
            return True, f"{len(logs)} Log-Dateien vorhanden - ueber Downloads laden"

        if head == "set_state":
            return self._set_state(text[len("set_state"):].strip(" :=").upper(), wait)

        if head == "camera_on":
            return self.start_camera()

        if head == "camera_off":
            return self.stop_camera()

        return False, f"Unbekannter Befehl: '{text}'"

    def _set_state(self, new_state, wait):
        if not new_state:
            return False, "set_state ohne Zielzustand"
        if new_state not in VALID_STATES:
            return False, (f"Zustand '{new_state}' nicht erlaubt "
                           f"(erlaubt: {', '.join(VALID_STATES)})")

        msg_system = SystemRequest()
        msg_system.source = "WIFI"
        msg_system.task = "SET_STATE"
        msg_system.message = new_state
        self.publish_system_request.publish(msg_system)

        if not wait:
            return True, f"set_state {new_state} gesendet"

        # Rueckmeldung abwarten: der command_node setzt den Zustand und
        # veroeffentlicht ihn auf operational_mode/current -> state_callback.
        deadline = time.time() + self.state_confirm_timeout
        while time.time() < deadline:
            if self.state == new_state:
                return True, f"Zustand {new_state} bestaetigt"
            time.sleep(0.1)
        return False, (f"Keine Bestaetigung fuer {new_state} (aktuell: {self.state}) "
                       f"- laeuft der command_node?")

    # ------------------------------------------------------------------
    # Kamera (web_video_server als Unterprozess)
    # ------------------------------------------------------------------
    def camera_running(self):
        return self.camera_proc is not None and self.camera_proc.poll() is None

    def _pkg_available(self, pkg):
        try:
            r = subprocess.run(["ros2", "pkg", "prefix", pkg],
                               capture_output=True, timeout=10)
            return r.returncode == 0
        except Exception:
            return False

    def start_camera(self):
        with self.camera_lock:
            if self.camera_running():
                return True, "Kamera-Stream laeuft bereits"
            if shutil.which("ros2") is None:
                return False, "ros2 nicht gefunden (ROS-Umgebung nicht geladen?)"
            if not self._pkg_available("web_video_server"):
                return False, ("Paket web_video_server fehlt "
                               "(sudo apt install ros-$ROS_DISTRO-web-video-server)")
            if self.count_publishers(self.camera_topic) == 0:
                return False, (f"Topic {self.camera_topic} hat keine Bildquelle "
                               f"- Kamera angeschlossen / Treiber gestartet?")
            try:
                self.camera_proc = subprocess.Popen(
                    ["ros2", "run", "web_video_server", "web_video_server",
                     "--ros-args", "-p", f"port:={self.camera_port}"],
                    start_new_session=True,
                )
            except OSError as e:
                return False, f"Stream konnte nicht starten: {e}"

            time.sleep(1.5)
            if self.camera_proc.poll() is not None:
                code = self.camera_proc.returncode
                self.camera_proc = None
                return False, f"Stream-Prozess sofort beendet (Code {code}, Port {self.camera_port} belegt?)"
            return True, f"Kamera-Stream laeuft auf Port {self.camera_port}"

    def stop_camera(self):
        with self.camera_lock:
            if not self.camera_running():
                self.camera_proc = None
                return True, "Kamera-Stream war nicht aktiv"
            try:
                os.killpg(os.getpgid(self.camera_proc.pid), signal.SIGINT)
                self.camera_proc.wait(timeout=3)
            except Exception:
                try:
                    os.killpg(os.getpgid(self.camera_proc.pid), signal.SIGKILL)
                except Exception:
                    pass
            self.camera_proc = None
            return True, "Kamera-Stream gestoppt"

    # ------------------------------------------------------------------
    # Dateien (Karte, Logs)
    # ------------------------------------------------------------------
    def map_info(self):
        if os.path.isfile(self.map_path):
            st = os.stat(self.map_path)
            return {"exists": True, "size": st.st_size, "mtime": _fmt_time(st.st_mtime)}
        return {"exists": False, "size": 0, "mtime": ""}

    def list_logs(self):
        if not os.path.isdir(self.log_dir):
            return []
        out = []
        for name in sorted(os.listdir(self.log_dir)):
            path = os.path.join(self.log_dir, name)
            if name.lower().endswith(".csv") and os.path.isfile(path):
                st = os.stat(path)
                out.append({"name": name, "size": st.st_size, "mtime": _fmt_time(st.st_mtime)})
        return out

    # ------------------------------------------------------------------
    # Webserver (Flask)
    # ------------------------------------------------------------------
    def _start_web_server(self):
        if Flask is None:
            self.get_logger().error("Flask fehlt: pip install flask - Webserver nicht gestartet")
            return

        app = Flask(__name__)
        node = self

        @app.route("/")
        def index():
            return PAGE.replace("__STATES__", str(VALID_STATES).replace("'", '"'))

        @app.route("/api/status")
        def api_status():
            with node.history_lock:
                history = list(node.history)
            return jsonify(
                state=node.state,
                camera=node.camera_running(),
                camera_port=node.camera_port,
                camera_topic=node.camera_topic,
                camera_topic_publishers=node.count_publishers(node.camera_topic),
                history=history,
            )

        @app.route("/api/cmd", methods=["POST"])
        def api_cmd():
            data = request.get_json(silent=True) or {}
            text = (data.get("cmd") or request.get_data(as_text=True) or "").strip()
            ok, msg = node.run_command(text, wait=True)
            return jsonify(ok=ok, msg=msg, cmd=text)

        @app.route("/api/files")
        def api_files():
            return jsonify(map=node.map_info(), logs=node.list_logs(), log_dir=node.log_dir)

        @app.route("/download/map")
        def download_map():
            if not os.path.isfile(node.map_path):
                abort(404, "Keine Karte vorhanden")
            return send_file(node.map_path, as_attachment=True,
                             download_name=os.path.basename(node.map_path))

        @app.route("/download/log/<name>")
        def download_log(name):
            name = os.path.basename(name)
            if name not in [f["name"] for f in node.list_logs()]:
                abort(404, "Log-Datei nicht gefunden")
            return send_file(os.path.join(node.log_dir, name), as_attachment=True,
                             download_name=name)

        @app.route("/download/logs.zip")
        def download_logs_zip():
            logs = node.list_logs()
            if not logs:
                abort(404, "Keine Log-Dateien vorhanden")
            buf = io.BytesIO()
            with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
                for f in logs:
                    z.write(os.path.join(node.log_dir, f["name"]), arcname=f["name"])
            buf.seek(0)
            stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return send_file(buf, mimetype="application/zip", as_attachment=True,
                             download_name=f"rover_logs_{stamp}.zip")

        threading.Thread(
            target=lambda: app.run(host="0.0.0.0", port=node.web_port,
                                   threaded=True, use_reloader=False),
            daemon=True,
        ).start()
        self.get_logger().info(f"Webserver auf Port {node.web_port}")


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