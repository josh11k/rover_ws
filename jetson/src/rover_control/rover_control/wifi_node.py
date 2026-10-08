import io
import math
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
from std_msgs.msg import String, Float64
from rcl_interfaces.msg import Log as RosLog

from rover_control_msgs.msg import LogMessage, OperationalMode, SystemRequest, MotorPosition

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

# rcl_interfaces/msg/Log Level -> Text
ROS_LEVELS = {10: "DEBUG", 20: "INFO", 30: "WARN", 40: "ERROR", 50: "FATAL"}

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
 /* --- Tabs + Debug-Ansicht --- */
 nav.tabs{display:flex;gap:4px;padding:8px 16px 0;background:#e5e7eb}
 nav.tabs button{margin:0;border-radius:6px 6px 0 0;border-bottom:none;background:#d1d5db}
 nav.tabs button.active{background:#f3f4f6;font-weight:600}
 #dbg{display:none;padding:16px}
 .stat{display:flex;flex-wrap:wrap;gap:8px;margin-bottom:14px}
 .stat div{background:#fff;border-radius:8px;padding:6px 10px;box-shadow:0 1px 3px #0002;font-size:13px;min-width:120px}
 .stat b{display:block;font-size:11px;color:#6b7280;font-weight:normal}
 .good{color:#15803d}.bad{color:#b91c1c}.warn{color:#b45309}
 .dbgwrap{display:grid;grid-template-columns:260px 1fr;gap:16px}
 @media(max-width:760px){.dbgwrap{grid-template-columns:1fr}}
 #filters label{display:block;font-size:13px;margin:4px 0}
 #dbg input[type=text]{width:100%;box-sizing:border-box}
 #dbglog{background:#111827;color:#e5e7eb;font-family:monospace;font-size:12px;height:62vh;
         overflow-y:auto;padding:8px;border-radius:6px;white-space:pre-wrap;word-break:break-word}
 #dbglog .src{color:#60a5fa}
 #dbglog .l-DEBUG{color:#9ca3af}#dbglog .l-WARN{color:#fbbf24}
 #dbglog .l-ERROR,#dbglog .l-FATAL{color:#f87171}
</style></head><body>
<header>
 <h1>Rover WiFi-Interface</h1>
 <span>Zustand: <span class="pill" id="state">?</span></span>
 <span>Kamera: <span class="pill" id="cam">?</span></span>
 <span>Verbindung: <span class="pill" id="conn">?</span></span>
</header>
<nav class="tabs">
 <button id="tab_ctl" class="active" onclick="showTab('ctl')">Steuerung</button>
 <button id="tab_dbg" onclick="showTab('dbg')">Debug</button>
</nav>
<main id="ctl">
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

<div id="dbg">
 <div class="stat" id="dbg_status"></div>
 <div class="dbgwrap">
  <section>
   <h2>Anzeigen</h2>
   <div id="filters"></div>
   <div style="margin-top:6px">
    <button onclick="setAll(true)">alle</button><button onclick="setAll(false)">keine</button>
   </div>
   <div class="muted" style="margin-top:10px">Mindest-Level:</div>
   <select id="minlvl" onchange="saveFilters();rerender()">
    <option>DEBUG</option><option selected>INFO</option><option>WARN</option><option>ERROR</option>
   </select>
   <div class="muted" style="margin-top:10px">Textfilter:</div>
   <input type="text" id="dbgtext" oninput="rerender()" placeholder="z. B. Motor 1">
   <label style="display:block;margin-top:10px"><input type="checkbox" id="autoscroll" checked> automatisch scrollen</label>
   <label style="display:block"><input type="checkbox" id="pause" onchange="if(!this.checked)rerender()"> Anzeige pausieren</label>
   <button onclick="clearView()" style="margin-top:8px">Anzeige leeren</button>
  </section>
  <section>
   <h2>Meldungen <span class="muted" id="dbgcount"></span></h2>
   <div id="dbglog"></div>
  </section>
 </div>
</div>

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

/* ================= Debug-Tab ================= */
// [Kategorie-ID, Beschriftung, standardmaessig an?]
var CATS=[
  ['stm_msg',     'STM: Meldungen (ACK/NACK/SET_STATE/MOTOR_LOG)', true],
  ['stm_text',    'STM: Debug-Text (ungerahmt)',                    true],
  ['stm_hb',      'STM: Heartbeat + ALIVE-ACK (periodisch)',        false],
  ['stm_hk',      'STM: Housekeeping-Block (alle 5 s)',             false],
  ['bridge_log',  'Bridge-Log (/log/com_stm)',                      false],
  ['ros_tracking','Tracking (position_rover_node)',                 true],
  ['ros_led',     'LED-Detektor (led_detector_node)',               true],
  ['ros_motor5',  'Motor 5 (xm430_node)',                           true],
  ['ros_command', 'command_node',                                   true],
  ['ros_bridge',  'stm_bridge_node',                                true],
  ['ros_other',   'andere Nodes',                                   false]
];
var LVL={DEBUG:0,INFO:1,WARN:2,ERROR:3,FATAL:4};
var MAXE=2000;
var dbgEntries=[], dbgLast=0, activeTab='ctl';

function loadFilters(){
  try{return JSON.parse(localStorage.getItem('roverDbgFilters')||'null');}catch(e){return null;}
}
function saveFilters(){
  var o={cats:{},lvl:el('minlvl').value};
  CATS.forEach(function(c){o.cats[c[0]]=el('f_'+c[0]).checked;});
  try{localStorage.setItem('roverDbgFilters',JSON.stringify(o));}catch(e){}
}
function buildFilters(){
  var s=loadFilters(), box=el('filters');
  CATS.forEach(function(c){
    var l=document.createElement('label'), cb=document.createElement('input');
    cb.type='checkbox';cb.id='f_'+c[0];
    cb.checked=(s && s.cats && (c[0] in s.cats))?s.cats[c[0]]:c[2];
    cb.onchange=function(){saveFilters();rerender();};
    l.appendChild(cb);l.appendChild(document.createTextNode(' '+c[1]));box.appendChild(l);
  });
  if(s && s.lvl){el('minlvl').value=s.lvl;}
}
function setAll(v){CATS.forEach(function(c){el('f_'+c[0]).checked=v;});saveFilters();rerender();}

function matches(e){
  var cb=el('f_'+e.cat);
  if(cb && !cb.checked)return false;
  if((LVL[e.lvl]||0) < LVL[el('minlvl').value])return false;
  var q=el('dbgtext').value.trim().toLowerCase();
  if(q && (e.src+' '+e.text).toLowerCase().indexOf(q)<0)return false;
  return true;
}
function lineEl(e){
  var d=document.createElement('div');d.className='l-'+e.lvl;
  var s=document.createElement('span');s.className='src';s.textContent=e.t+' ['+e.src+'] ';
  d.appendChild(s);d.appendChild(document.createTextNode(e.text));
  return d;
}
function updateCount(){el('dbgcount').textContent='('+el('dbglog').childElementCount+' angezeigt, '+dbgEntries.length+' gepuffert)';}
function scrollDown(){if(el('autoscroll').checked){var b=el('dbglog');b.scrollTop=b.scrollHeight;}}
function rerender(){
  var box=el('dbglog'), f=document.createDocumentFragment();
  box.innerHTML='';
  dbgEntries.forEach(function(e){if(matches(e))f.appendChild(lineEl(e));});
  box.appendChild(f);updateCount();scrollDown();
}
function clearView(){dbgEntries=[];rerender();}

function esc(t){return String(t).replace(/[&<>"]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c];});}
function ageTxt(ts,now){return ts?('vor '+Math.max(0,now-ts).toFixed(1)+' s'):'nie';}
function fresh(ts,now,limit){return ts && (now-ts)<limit;}
function sbox(title,val,cls){return '<div><b>'+esc(title)+'</b><span class="'+(cls||'')+'">'+esc(val)+'</span></div>';}

function renderStatus(s,now){
  var h='';
  h+=sbox('STM-Verbindung (letzte Zeile)', ageTxt(s.last_stm_line,now), fresh(s.last_stm_line,now,3)?'good':'bad');
  h+=sbox('ALIVE-ACK vom STM', ageTxt(s.last_alive_ack,now), fresh(s.last_alive_ack,now,15)?'good':'bad');
  h+=sbox('STM-State', s.stm_state, s.stm_state==='SAFE'?'bad':'');
  h+=sbox('STM-Fault', s.stm_fault, s.stm_fault==='NONE'?'good':(s.stm_fault==='?'?'':'bad'));
  h+=sbox('Letztes NACK', s.last_nack?(s.last_nack+' ('+ageTxt(s.last_nack_t,now)+')'):'-', s.last_nack?'warn':'');
  h+=sbox('Jetson-Modus', s.jetson_state, '');
  h+=sbox('Tracking', s.tracking+(s.tracking_t?' ('+ageTxt(s.tracking_t,now)+')':''),
          /TRACKING/.test(s.tracking)?'good':(/SUCHE/.test(s.tracking)?'warn':''));
  h+=sbox('Pan (Motor 5)', s.pan_deg===null?'-':(s.pan_deg.toFixed(1)+' Grad ('+ageTxt(s.pan_t,now)+')'),
          fresh(s.pan_t,now,1)?'good':'bad');
  h+=sbox('Tilt (Motor 1)', s.tilt_raw===null?'-':(s.tilt_raw+' raw ('+ageTxt(s.tilt_t,now)+')'),
          fresh(s.tilt_t,now,12)?'good':'bad');
  el('dbg_status').innerHTML=h;
}

async function pollDebug(){
  if(activeTab!=='dbg')return;
  try{
    var j=await (await fetch('/api/debug?since='+dbgLast)).json();
    if(j.last_id < dbgLast){  // wifi_node wurde neu gestartet -> von vorne
      dbgLast=0;dbgEntries=[];rerender();return;
    }
    dbgLast=j.last_id;
    renderStatus(j.status,j.now);
    if(!j.entries.length)return;
    dbgEntries=dbgEntries.concat(j.entries);
    var over=dbgEntries.length-MAXE;
    if(over>0){dbgEntries=dbgEntries.slice(over);}
    if(el('pause').checked)return;
    if(over>0){rerender();return;}
    var box=el('dbglog'), f=document.createDocumentFragment();
    j.entries.forEach(function(e){if(matches(e))f.appendChild(lineEl(e));});
    box.appendChild(f);updateCount();scrollDown();
  }catch(e){}
}

function showTab(t){
  activeTab=t;
  el('ctl').style.display=(t==='ctl')?'':'none';
  el('dbg').style.display=(t==='dbg')?'block':'none';
  el('tab_ctl').className=(t==='ctl')?'active':'';
  el('tab_dbg').className=(t==='dbg')?'active':'';
  if(t==='dbg'){pollDebug();}
}

buildStateButtons();buildFilters();refresh();loadFiles();
setInterval(refresh,2000);setInterval(loadFiles,15000);setInterval(pollDebug,1000);
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

        # ---------------- Debug-Ansicht  ----------------
        # Liest NICHT den seriellen Port -- nur ROS-Topics. Den Port hat
        # ausschliesslich die stm_bridge_node offen.
        self.debug_log = deque(maxlen=2000)
        self.debug_lock = threading.Lock()
        self.debug_next_id = 1
        self._in_hk_block = False
        self.dbg_status = {
            "last_stm_line": None,
            "last_alive_ack": None,
            "stm_state": "?",
            "stm_fault": "?",
            "last_nack": "",
            "last_nack_t": None,
            "tracking": "?",
            "tracking_t": None,
            "pan_deg": None,
            "pan_t": None,
            "tilt_raw": None,
            "tilt_t": None,
        }

        # ---------------- Subscriber ----------------
        self.sub_wifi = self.create_subscription(
            String, "/wifi/incoming_message", self.incoming_callback, 10)
        self.sub_wifi_trigger = self.create_subscription(
            String, "/trigger/wifi", self.incoming_callback, 10)
        self.sub_state = self.create_subscription(
            OperationalMode, "operational_mode/current", self.state_callback, 10)

        # Quellen fuer die Debug-Ansicht
        self.sub_stm_lines = self.create_subscription(
            String, "/stm/raw_lines", self.stm_line_callback, 100)
        self.sub_com_stm = self.create_subscription(
            LogMessage, "/log/com_stm", self.com_stm_callback, 50)
        self.sub_rosout = self.create_subscription(
            RosLog, "/rosout", self.rosout_callback, 200)
        self.sub_pan = self.create_subscription(
            Float64, "/xm430_node/current_position", self.pan_callback, 10)
        self.sub_tilt = self.create_subscription(
            MotorPosition, "/motor_position/current_position", self.tilt_callback, 10)

        # ---------------- Publisher ----------------
        self.pub_wifi = self.create_publisher(String, "/wifi/outgoing_message", 10)
        self.publish_wifi_log = self.create_publisher(LogMessage, "/log/wifi", 10)
        self.publish_operational_log = self.create_publisher(LogMessage, "/log/operations", 10)
        self.publish_system_request = self.create_publisher(
            SystemRequest, "/wifi_node/system_request", 10)

        self._start_web_server()


    # ROS-Seite
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


    # Debug-Ansicht 
    def _dbg_add(self, cat, level, src, text):
        now = time.time()
        entry = {
            "t": datetime.fromtimestamp(now).strftime("%H:%M:%S.%f")[:-3],
            "cat": cat,
            "lvl": level,
            "src": src,
            "text": text,
        }
        with self.debug_lock:
            entry["id"] = self.debug_next_id
            self.debug_next_id += 1
            self.debug_log.append(entry)

    def stm_line_callback(self, msg):
        """Eine ganze Zeile vom STM (von der Bridge auf /stm/raw_lines)."""
        line = msg.data.rstrip()
        now = time.time()
        st = self.dbg_status
        st["last_stm_line"] = now
        level = "INFO"

        if line.startswith(">>HOUSE_KEEPING_DATA"):
            self._in_hk_block = True
            cat = "stm_hk"
        elif self._in_hk_block and not line.startswith(">>"):
            # Zeile innerhalb des Housekeeping-Blocks
            cat = "stm_hk"
            if line.endswith("<<"):
                self._in_hk_block = False
            m = re.match(r"STM Status:\s*(\S+)", line)
            if m:
                st["stm_state"] = m.group(1)
            m = re.match(r"STM Fault:\s*(\S+)", line)
            if m:
                st["stm_fault"] = m.group(1)
        elif line.startswith(">>"):
            # neues gerahmtes Paket beendet einen evtl. abgeschnittenen HK-Block
            self._in_hk_block = False
            if line.startswith(">>HB"):
                cat = "stm_hb"
                m = re.match(r">>HB:\s*(\w+)", line)
                if m:
                    st["stm_state"] = m.group(1)
            elif line.startswith(">>ACK, ALIVE"):
                cat = "stm_hb"
                st["last_alive_ack"] = now
            else:
                cat = "stm_msg"
                if line.startswith(">>NACK"):
                    level = "WARN"
                    st["last_nack"] = line.strip("<> ").split(",", 1)[-1].strip()
                    st["last_nack_t"] = now
                m = re.match(r">>SET_STATE\s+(\w+)", line)
                if m:
                    st["stm_state"] = m.group(1)
        else:
            # ungerahmter Debug-Text, z.B. "SAFE: braking all motors"
            cat = "stm_text"
            low = line.lower()
            if "fail" in low or "error" in low:
                level = "ERROR"
            elif "warn" in low or "timeout" in low or "unavailable" in low:
                level = "WARN"

        self._dbg_add(cat, level, "STM", line)

    def com_stm_callback(self, msg):
        level = "ERROR" if msg.event == "ERROR" else "INFO"
        self._dbg_add("bridge_log", level, f"com_stm/{msg.source}", msg.message)

    def rosout_callback(self, msg):
        name = msg.name
        if "position_rover" in name:
            cat = "ros_tracking"
            self._update_tracking_status(msg.msg)
        elif "led_detector" in name:
            cat = "ros_led"
        elif "xm430" in name:
            cat = "ros_motor5"
        elif "command" in name:
            cat = "ros_command"
        elif "stm_bridge" in name:
            cat = "ros_bridge"
        else:
            cat = "ros_other"
        self._dbg_add(cat, ROS_LEVELS.get(msg.level, str(msg.level)), name, msg.msg)

    def _update_tracking_status(self, text):
        """Tracking-Zustand aus den Logmeldungen des position_rover_node ableiten."""
        st = self.dbg_status
        if "gefunden" in text:
            st["tracking"] = "TRACKING (Pattern gefunden)"
        elif "verloren" in text:
            st["tracking"] = "SUCHE (Pattern verloren)"
        elif "naechste Pan-Position" in text:
            m = re.search(r"(-?\d+(?:\.\d+)?) deg", text)
            st["tracking"] = "SUCHE" + (f" (Ziel {m.group(1)} Grad)" if m else "")
        elif "ohne Fund" in text:
            st["tracking"] = "SUCHE (neuer Durchlauf)"
        elif "abgeschlossen" in text:
            st["tracking"] = "SUCHE beendet (nichts gefunden)"
        elif text.endswith(": ON"):
            st["tracking"] = "AN (wartet auf Daten)"
        elif text.endswith(": OFF"):
            st["tracking"] = "AUS"
        else:
            return
        st["tracking_t"] = time.time()

    def pan_callback(self, msg):
        self.dbg_status["pan_deg"] = math.degrees(msg.data)
        self.dbg_status["pan_t"] = time.time()

    def tilt_callback(self, msg):
        self.dbg_status["tilt_raw"] = msg.motor1
        self.dbg_status["tilt_t"] = time.time()


    # Befehlsausfuehrung (liefert immer (ok, text))
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


    # Kamera (web_video_server als Unterprozess)
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


    # Dateien (Karte, Logs)
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


    # Webserver (Flask)
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

        # Debug-Daten -- alle Eintraege mit id > since + Statusleiste
        @app.route("/api/debug")
        def api_debug():
            try:
                since = int(request.args.get("since", 0))
            except ValueError:
                since = 0
            with node.debug_lock:
                entries = [e for e in node.debug_log if e["id"] > since]
                last_id = node.debug_next_id - 1
            status = dict(node.dbg_status)
            status["jetson_state"] = node.state
            return jsonify(now=time.time(), last_id=last_id,
                           entries=entries[-500:], status=status)

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