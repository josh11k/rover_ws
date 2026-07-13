import rclpy
from rclpy.node import Node
import serial
import time

# Hier nutzen wir deine eigene Custom Message für den Service und das Topic
from rover_control_msgs.srv import SetOperationalMode as SetModeSrv
from rover_control_msgs.msg import SetOperationalMode as SetModeMsg

class STMBridgeNode(Node):
    def __init__(self):
        super().__init__('stm_bridge_node')
        
        # 1. Parameter für die Hardware
        self.port = '/dev/ttyACM0'  # Für Jetson ggf. anpassen (z.B. /dev/ttyUSB0)
        self.baudrate = 115200

        # 2. ROS 2 Kommunikations-Schnittstellen einrichten
        # Wir erstellen einen Service, der deine Custom Message nutzt
        self.srv = self.create_service(
            SetModeSrv, 
            '/stm/set_mode_on_stm', 
            self.set_mode_on_STM
        )
        
        # Ein Publisher, um das erfolgreiche Feedback ins ROS-Netz zu funken
        self.mode_pub = self.create_publisher(
            SetModeMsg, 
            '/stm/set_mode_on_jetson',
            10
        )

        self.timer = self.create_timer(0.01, self.set_mode_on_Jetson)

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

    def set_mode_on_STM(self, request, response):
        """Wird aufgerufen, wenn die Command Node den Service anfunkt"""
        if self.ser is None or not self.ser.is_open:
            response.success = False
            response.message = "Serielle Verbindung zum STM32 ist nicht offen!"
            return response

        # Kohärente Nutzung: Wir holen den Modus aus deiner Custom Message
        requested_mode = request.mode  # Angenommen, dein Feld in der .srv/.msg Datei heißt 'mode'
        command = f"SET:{requested_mode}\n"
        
        try:
            # 1. Befehl EINMALIG senden
            self.ser.write(command.encode('utf-8'))
            self.get_logger().info(f"Befehl gesendet: {command.strip()}")
            
            # 2. Warten, bis das 'OK' oder Feedback vom STM32 zurückkommt
            feedback = self.ser.readline().decode('utf-8').strip()
            
            if feedback == "OK" or feedback == f"MODE:{requested_mode}":
                self.get_logger().info(f"STM32 hat den Modus bestätigt: {feedback}")
                response.success = True
                response.message = f"Modus erfolgreich geändert auf {requested_mode}"
                
            else:
                self.get_logger().warn(f"Unerwartete Antwort vom STM32: {feedback}")
                response.success = False
                response.message = f"Falsches Feedback vom STM32 erhalten: {feedback}"
                
        except Exception as e:
            self.get_logger().error(f"Fehler bei der Kommunikation: {e}")
            response.success = False
            response.message = str(e)
            
        return response
    
    def set_mode_on_Jetson(self):
        """Prüft permanent den seriellen Puffer auf eingehende Daten vom STM32"""
        if self.ser is None or not self.ser.is_open:
            return

        try:
            # Wenn Bytes im USB-Puffer bereitliegen...
            if self.ser.in_waiting > 0:
                # Zeile lesen (bis zum \n) und Whitespaces entfernen
                line = self.ser.readline().decode('utf-8').strip()
                
                if not line:
                    return

                self.get_logger().info(f"Received raw data from STM32: {line}")

                # Überprüfung, ob die Nachricht das richtige Präfix hat (z.B. "MODE:MANUAL")
                # Isoaltes Message received. Message should be between 00-99
                if line.startswith("MODE:"):
                    # Schneidet das "MODE:" ab und isoliert den Modus-String (z.B. "MANUAL")
                    stm_mode = line.split(":")[1] 
                    
                    self.get_logger().info(f"STM32 reported active mode: {stm_mode}")

                    # Nachricht für das ROS 2 Topic vorbereiten
                    msg = SetModeMsg()
                    msg.mode = stm_mode
                    
                    # Nachricht ins ROS-Netzwerk jagen (jetzt können es Kameras/CommandNode lesen)
                    self.mode_pub.publish(msg)

        except Exception as e:
            self.get_logger().error(f"Error reading from serial port: {e}")

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