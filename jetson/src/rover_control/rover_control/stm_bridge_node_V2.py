import rclpy
from rclpy.node import Node
import serial
import time
import codecs
from std_msgs.msg import String

from rover_control_msgs.srv import SetOperationalMode as SetModeSrv
from rover_control_msgs.msg import SetOperationalMode as SetModeMsg
from rover_control_msgs.msg import LogMessage, OperationalMode, SystemRequest, Housekeeping, MotorPosition

class STMBridgeNode(Node):
    def __init__(self):
        super().__init__('stm_bridge_node')

        # 1. Parameter für die Hardware
        self.port = '/dev/ttyACM0'  # Für Jetson ggf. anpassen (z.B. /dev/ttyUSB0)
        self.baudrate = 115200

        # Puffer für empfangene, noch nicht vollständig geparste Daten vom
        # STM32 -- von receive_message() befüllt, sobald das angeschlossen wird.
        self.buffer = ""

        # UTF-8 inkrementell dekodieren
        self.decoder = codecs.getincrementaldecoder('utf-8')(errors='replace')
        self.line_buffer = ""


        # 2. Incoming Messages
        self.subscription = self.create_subscription(
            SystemRequest,
            '/command/system_request',
            self.prep_message_callback,
            10
        )

        self.motor_position_subscription = self.create_subscription(
            MotorPosition,
            '/motor_position/goal_position',
            self.send_motor_position_callback,
            10
        )


        # 3. Outgoing Messages (eventuell in receive message)
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

        self.publish_system_request = self.create_publisher(
            SystemRequest,
            '/bridge_node/system_request',
            10
            )

        self.publish_housekeeping_data = self.create_publisher(
            Housekeeping,
            '/log/housekeeping',
            50
            )

        self.publish_motor_position = self.create_publisher(
            MotorPosition,
            '/motor_position/current_position',
            10
            )

        # jede ganze Zeile vom STM (gerahmt und ungerahmt) -- fuer die
        # Debug-Ansicht im wifi_node. Nur die Bridge liest den Port.
        self.publish_raw_line = self.create_publisher(
            String,
            '/stm/raw_lines',
            100
            )

        # 3. Serielle Verbindung zum STM32 EINMALIG öffnen
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                timeout=0.1
            )
            self.get_logger().info(f"Erfolgreich mit STM32 verbunden via {self.port}")

            # Dem STM32 2 Sekunden Zeit geben, nach dem Verbindungs-Reset hochzufahren
            time.sleep(2)
        except serial.SerialException as e:
            self.get_logger().error(f"Konnte serielle Schnittstelle nicht öffnen: {e}")
            self.ser = None

        # Timer, der alle 10 ms receive_message aufruft
        self.read_timer = self.create_timer(0.01, self.receive_message)

    def prep_message_callback(self, msg):
        msg_log = LogMessage()

        if msg.task == "ALIVE":
            msg_log.source = "JETSON"
            msg_log.event = "INFO"
            msg_log.message = f"Send heartbeat to STM32: {msg.message}"
            self.publish_operational_log.publish(msg_log)
            self.publish_com_stm_log.publish(msg_log)
            command = f">>{msg.task}: {msg.message}<<"

        elif msg.task == "SET_STATE":
            msg_log.source = "JETSON"
            msg_log.event = "INFO"
            msg_log.message = f"Request to set STM32 mode to {msg.message}"
            self.publish_operational_log.publish(msg_log)
            self.publish_com_stm_log.publish(msg_log)
            command = f">>{msg.task}: {msg.message}<<"

        elif msg.task == "ERROR":
            msg_log.source = "JETSON"
            msg_log.event = "ERROR"
            msg_log.message = f"Error reported: {msg.message}"
            self.publish_operational_log.publish(msg_log)
            self.publish_com_stm_log.publish(msg_log)
            command = f">>{msg.task}: {msg.message}<<"

        else:
            # unbekannter Task -> nichts senden 
            self.get_logger().warn(f"Unbekannter Task '{msg.task}' -- nicht an STM32 gesendet.")
            return

        self.send_message(command)

    def send_motor_position_callback(self, msg):
        # MotorPosition hat nur motor1..motor4 -- 'msg.task = ...'
        # Der Jetson steuert nur motor1 (Tilt), motor2-4 werden ignoriert.
        msg_log = LogMessage()
        msg_log.source = "JETSON"
        msg_log.event = "INFO"
        msg_log.message = f"Motor command sent: Motor 1 {msg.motor1}"

        self.publish_operational_log.publish(msg_log)
        self.publish_com_stm_log.publish(msg_log)

        command = f">>SET_MOTOR: {msg.motor1}<<"
        self.send_message(command)



    def send_message(self, msg): # Kaum angefangen

        if self.ser is None or not self.ser.is_open:
            self.get_logger().error("Serielle Verbindung zum STM32 ist nicht offen!")
            return  #nicht versuchen, auf einen geschlossenen Port zu schreiben

        try:
            # 1. Befehl EINMALIG senden
            self.ser.write((msg + "\n").encode('utf-8'))
            self.get_logger().info(f"Befehl gesendet: {msg.strip()}")
            self.publish_operational_log.publish(LogMessage(source="JETSON", event="INFO", message=f"Command sent to STM32"))
            self.publish_com_stm_log.publish(LogMessage(source="JETSON", event="INFO", message=f"Command sent to STM32"))

        except Exception as e:
            self.get_logger().error(f"Fehler bei der Kommunikation: {e}")
            self.publish_operational_log.publish(LogMessage(source="JETSON", event="ERROR", message=f"Communication error: {e}"))
            self.publish_com_stm_log.publish(LogMessage(source="JETSON", event="ERROR", message=f"Communication error: {e}"))




    def receive_message(self):  # kein Argument mehr, wird vom Timer aufgerufen

        # nichts tun, wenn der Port nicht offen ist
        if self.ser is None or not self.ser.is_open:
            return

        if self.ser.in_waiting > 0:
            # 1. Alle verfügbaren Zeichen in den Puffer lesen
            # inkrementeller Decoder statt .decode(errors='ignore')
            chunk = self.decoder.decode(self.ser.read(self.ser.in_waiting))
            # debug statt info -- die Rohdaten laufen jetzt zeilenweise
            # ueber /stm/raw_lines, sonst wuerde /rosout alle 10 ms geflutet.
            self.get_logger().debug(f"RAW: {chunk!r}")
            self.buffer += chunk

            # ganze Zeilen auf /stm/raw_lines publizieren
            self.line_buffer += chunk
            while "\n" in self.line_buffer:
                line, self.line_buffer = self.line_buffer.split("\n", 1)
                line = line.rstrip("\r")
                if line.strip():
                    self.publish_raw_line.publish(String(data=line))
            if len(self.line_buffer) > 2000:
                # Schutz: sehr lange Zeile ohne Zeilenende trotzdem ausgeben
                self.publish_raw_line.publish(String(data=self.line_buffer))
                self.line_buffer = ""

            # 2. Prüfen, ob ein vollständiges Paket vorhanden ist
            while ">>" in self.buffer and "<<" in self.buffer:
                start_pos = self.buffer.find(">>")
                end_pos = self.buffer.find("<<")

                # Sicherheits-Check: Falls $END vor $START steht (verstümmelte Daten)
                if end_pos < start_pos:
                    self.buffer = self.buffer[end_pos + len("<<"):]
                    continue

                # Payload zwischen $START und $END herausschneiden
                payload_start = start_pos + len(">>")
                raw_payload = self.buffer[payload_start:end_pos]

                # Verarbeiteten Teil aus dem Puffer löschen
                self.buffer = self.buffer[end_pos + len("<<"):]

                # 3. Payload zeilenweise parsen
                # Hier kommt serial_msg_processing.py ins Spiel, enthält Funtionen um Nachricht zu verarbeiten
                # debug statt info (Heartbeat jede Sekunde wuerde /rosout fluten)
                self.get_logger().debug(f"Received raw data from STM32: {raw_payload}")

                # Fehler beim Parsen abfangen, damit die Node weiterläuft
                try:
                    self.process_msg(raw_payload)
                except Exception as e:
                    self.get_logger().warn(f"Konnte Paket nicht verarbeiten: {raw_payload!r} ({e})")


# Functions for processing incoming messages
    def process_msg(self, payload):
        if payload.startswith("HB"):
            # Bei ',' teilen -> ["HB: STANDBY", " t = 123456.4567 s"]
            parts = payload.split(",")
            msg = LogMessage()

            # State extrahieren: Nach ':' schneiden und Leerzeichen entfernen
            state = parts[0].split(":")[1].strip()  # Ergebnis: "STANDBY"

            # Zeit extrahieren: Nach '=' schneiden, 's' entfernen und zu float wandeln
            time_str = parts[1].split("=")[1].replace("s", "").strip()

            text = f"{time_str}:STM32 in {state} mode"

            msg.source = "STM32"
            msg.event = "INFO"
            msg.message = text

            self.publish_operational_log.publish(msg)
            self.publish_com_stm_log.publish(msg)

        elif payload.startswith("SET_STATE"):
            parts = payload.split(" ")

            msg_system = SystemRequest()
            msg_system.source = "STM32"
            msg_system.task = "SET_STATE"
            msg_system.message = f"{parts[1]}"

            msg_log = LogMessage()
            msg_log.source = "STM32"
            msg_log.event = "INFO"
            msg_log.message = f"Request to set mode to {parts[1]}"

            self.publish_operational_log.publish(msg_log)
            self.publish_com_stm_log.publish(msg_log)
            self.publish_system_request.publish(msg_system)

        elif payload.startswith("ACK"):
            # STM sendet ">>ACK, <WAS><<" (mit Leerzeichen nach dem
            # Komma), z.B. "ACK, ALIVE", "ACK, MOTOR", "ACK, SET_STATE".
            parts = payload.split(",", 1)
            what = parts[1].strip() if len(parts) > 1 else ""

            msg = LogMessage()
            msg.source = "STM32"
            msg.event = "INFO"
            msg.message = f"STM32 acknowledged: {what}"

            self.publish_com_stm_log.publish(msg)
            if what != "ALIVE":
                # ALIVE-ACK kommt alle 5 s -> /log/operations nicht zumuellen
                self.publish_operational_log.publish(msg)

        elif payload.startswith("NACK"):
            msg = LogMessage()
            msg.source = "STM32"
            msg.event = "ERROR"
            parts = payload.split(",", 1)
            msg.message = parts[1].strip() if len(parts) > 1 else payload  

            self.publish_operational_log.publish(msg)
            self.publish_com_stm_log.publish(msg)

        elif payload.startswith("REBOOT"):
            msg_log = LogMessage()
            msg_log.source = "STM32"
            msg_log.event = "ERROR"
            msg_log.message = f"STM32 asks for reboot."

            msg_system = SystemRequest()
            msg_system.source = "STM32"
            msg_system.task = "REBOOT"
            msg_system.message = f"STM32 asks for reboot."

            self.publish_operational_log.publish(msg_log)
            self.publish_com_stm_log.publish(msg_log)
            self.publish_system_request.publish(msg_system)

        elif payload.startswith("BOOT"):
            parts = payload.split(",")

            msg = LogMessage()
            msg.source = "STM32"
            msg.event = "INFO"
            msg.message = f"STM32 booted with STATUS: {parts[1]}"

            self.publish_operational_log.publish(msg)
            self.publish_com_stm_log.publish(msg)

        elif payload.startswith("SHUTDOWN"):
            msg_log = LogMessage()
            msg_log.source = "STM32"
            msg_log.event = "ERROR"
            msg_log.message = f"STM32 asks for shutdown."

            msg_system = SystemRequest()
            msg_system.source = "STM32"
            msg_system.task = "SHUTDOWN"
            msg_system.message = f"STM32 asks for shutdown."

            self.publish_operational_log.publish(msg_log)
            self.publish_com_stm_log.publish(msg_log)
            self.publish_system_request.publish(msg_system)


        elif payload.startswith("HOUSE_KEEPING_DATA"):
            lines = [l.strip() for l in payload.splitlines()[1:] if l.strip()]
            motor_positions = {}

            for line in lines:
                parts = [p.strip() for p in line.split(":", 2)]

                if len(parts) == 3:
                    # z.B. "Motor 1: Position: NA"
                    component, type_, value = parts
                elif len(parts) == 2:
                    # z.B. "Time: 5803s" oder "STM Status: STANDBY"
                    component, type_, value = "STM", parts[0], parts[1]
                else:
                    continue

                msg_hkd = Housekeeping()
                msg_hkd.source = "STM32"
                msg_hkd.component = component
                msg_hkd.type = type_
                msg_hkd.value = value
                self.publish_housekeeping_data.publish(msg_hkd)

                # Motorpositionen merken (nur numerische Werte)
                if component.startswith("Motor ") and type_ == "Position":
                    try:
                        motor_positions[int(component.split()[1])] = int(value)
                    except ValueError:
                        pass   # "NA"

            msg_log = LogMessage()
            msg_log.source = "STM32"
            msg_log.event = "INFO"
            msg_log.message = "Housekeeping data received"   # ggf. .message, je nach .msg
            self.publish_operational_log.publish(msg_log)
            self.publish_com_stm_log.publish(msg_log)

            # publishen, sobald Motor 1 (Tilt) gültig ist -- der Jetson
            # braucht nur motor1. Fehlende Motoren 2-4 = -1 (unbekannt).
            if 1 in motor_positions:
                msg_motor = MotorPosition()
                msg_motor.motor1 = motor_positions[1]
                msg_motor.motor2 = motor_positions.get(2, -1)
                msg_motor.motor3 = motor_positions.get(3, -1)
                msg_motor.motor4 = motor_positions.get(4, -1)
                self.publish_motor_position.publish(msg_motor)





def main(args=None):
    rclpy.init(args=args)
    node = STMBridgeNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Beim Beenden der Node die serielle Schnittstelle sauber schließen
        if node.ser and node.ser.is_open:
            node.ser.close()
            node.get_logger().info("Serielle Verbindung geschlossen.")
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()