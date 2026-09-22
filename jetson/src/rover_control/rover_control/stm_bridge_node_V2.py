import rclpy
from rclpy.node import Node
import serial
import time

# Hier nutzen wir deine eigene Custom Message für den Service und das Topic
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

        # 2. Incoming Messages
        # message beinhaltet task und ruft send_message auf
        self.subscription = self.create_subscription(
            SystemRequest,
            '/command/system_request',
            self.prep_message_callback,
            10
        )

        self.motor_position_subscription = self.create_subscription(
            MotorPosition,
            '/motor_position/new',
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
            '/motor_position/current',
            10
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

    def prep_message_callback(self, msg):
        msg_log = LogMessage()

        if msg.task == "ALIVE":
            msg_log.source = "JETSON"
            msg_log.event = "INFO"
            msg_log.details = f"Send heartbeat to STM32: {msg.message}"
            self.publish_operational_log.publish(msg_log)
            self.publish_com_stm_log.publish(msg_log)

        if msg.task == "SET_STATE":
            msg_log.source = "JETSON"
            msg_log.event = "INFO"
            msg_log.details = f"Request to set STM32 mode to {msg.message}"
            self.publish_operational_log.publish(msg_log)  
            self.publish_com_stm_log.publish(msg_log)

        if msg.task == "ERROR":
            msg_log.source = "JETSON"
            msg_log.event = "ERROR"
            msg_log.details = f"Error reported: {msg.message}"
            self.publish_operational_log.publish(msg_log)
            self.publish_com_stm_log.publish(msg_log)

    def send_motor_position_callback(self, msg):
        msg_log = LogMessage()
        msg_log.source = "JETSON"
        msg_log.event = "INFO"
        msg_log.details = f"Motor command sent: Motor 1 {msg.motor1}, Motor 2 {msg.motor2}, Motor 3 {msg.motor3}, Motor 4 {msg.motor4}, Motor 5 {msg.motor5}"

        self.publish_operational_log.publish(msg_log)
        self.publish_com_stm_log.publish(msg_log)

        msg.task = "SET_MOTOR:"
        command = f">>{msg.task} {msg.motor1}, {msg.motor2}, {msg.motor3}, {msg.motor4}, {msg.motor5}<<"
        self.send_message(command)



    def send_message(self, msg): # Kaum angefangen

        if self.ser is None or not self.ser.is_open:
            self.get_logger().error("Serielle Verbindung zum STM32 ist nicht offen!")

        # Kohärente Nutzung: Wir holen den Modus aus deiner Custom Message
        # msg = task.task  # Angenommen, dein Feld in der .srv/.msg Datei heißt 'mode'
        # Baut die message für den STM zusammen
        #    command = f"SET:{msg}\n"

        try:
            # 1. Befehl EINMALIG senden
            self.ser.write(msg.encode('utf-8'))
            self.get_logger().info(f"Befehl gesendet: {msg.strip()}")
            self.publish_operational_log.publish(LogMessage(source="JETSON", event="INFO", details=f"Command sent to STM32"))
            self.publish_com_stm_log.publish(LogMessage(source="JETSON", event="INFO", details=f"Command sent to STM32"))
                       
        except Exception as e:
            self.get_logger().error(f"Fehler bei der Kommunikation: {e}")
            self.publish_operational_log.publish(LogMessage(source="JETSON", event="ERROR", details=f"Communication error: {e}"))
            self.publish_com_stm_log.publish(LogMessage(source="JETSON", event="ERROR", details=f"Communication error: {e}"))
  



    def receive_message(self, task):

        if self.ser.in_waiting > 0:
            # 1. Alle verfügbaren Zeichen in den Puffer lesen
            self.buffer += self.ser.read(self.ser.in_waiting).decode('utf-8', errors='ignore')

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
                self.get_logger().info(f"Received raw data from STM32: {raw_payload}")

                self.process_msg(raw_payload)


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
            msg.details = text
    
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
            msg_log.details = f"Request to set mode to {parts[1]}"
            
            self.publish_operational_log.publish(msg_log)
            self.publish_com_stm_log.publish(msg_log)
            self.publish_system_request.publish(msg_system)

        elif payload.startswith("ACK,MOTOR"):
            msg = LogMessage()
            msg.source = "STM32"
            msg.event = "INFO"
            msg.details = f"Motor command acknowledged by STM32"

            self.publish_operational_log.publish(msg)
            self.publish_com_stm_log.publish(msg)

        elif payload.startswith("NACK"):
            msg = LogMessage()
            msg.source = "STM32"
            msg.event = "ERROR"
            parts = payload.split(",")
            msg.details = f"{parts[1]}"

            self.publish_operational_log.publish(msg)
            self.publish_com_stm_log.publish(msg)

        elif payload.startswith("REBOOT"):
            msg_log = LogMessage()
            msg_log.source = "STM32"
            msg_log.event = "ERROR"
            msg_log.details = f"STM32 asks for reboot."

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
            msg.details = f"STM32 booted with STATUS: {parts[1]}"

            self.publish_operational_log.publish(msg)
            self.publish_com_stm_log.publish(msg)

        elif payload.startswith("SHUTDOWN"):
            msg_log = LogMessage()
            msg_log.source = "STM32"
            msg_log.event = "ERROR"
            msg_log.details = f"STM32 asks for shutdown."

            msg_system = SystemRequest()
            msg_system.source = "STM32"
            msg_system.task = "SHUTDOWN"
            msg_system.message = f"STM32 asks for shutdown."

            self.publish_operational_log.publish(msg_log)
            self.publish_com_stm_log.publish(msg_log)
            self.publish_system_request.publish(msg_system)

        elif payload.startswith("HOUSE_KEEPING_DATA"):
            parts = payload.split(":")
            msg_log = LogMessage()
            msg_log.source = "STM32"
            msg_log.event = "INFO"
            msg_log.details = f"Housekeeping data received"

            msg_hkd = Housekeeping()
            msg_hkd.source = "STM32"

            for i in range(1, len(parts) - 1, 2):    
                 # Werte zuweisen
                msg_hkd.component = parts[i]
                msg_hkd.value = parts[i+1]
                self.publish_housekeeping_data.publish(msg_hkd)
            
            self.publish_operational_log.publish(msg)
            self.publish_com_stm_log.publish(msg)

            # Make Motor Values:
            msg_motor = MotorPosition()
            msg_motor.motor1 = int(parts[23])
            msg_motor.motor2 = int(parts[25])
            msg_motor.motor3 = int(parts[27])
            msg_motor.motor4 = int(parts[29])
            msg_motor.motor5 = int(parts[31])

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