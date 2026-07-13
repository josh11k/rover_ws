import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
import numpy as np

class FakeRealSense(Node):
    def __init__(self):
        super().__init__('fake_realsense_node')
        # Wir veröffentlichen auf dem exakt gleichen Topic wie die echte Kamera
        self.publisher_ = self.create_publisher(Image, '/camera/camera/depth/image_rect_raw', 10)
        self.timer = self.create_timer(0.5, self.timer_callback)
        self.get_logger().info('Fake RealSense Node gestartet. Sende Mock-Tiefendaten...')

    def timer_callback(self):
        msg = Image()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'camera_depth_optical_frame'
        
        # Simulation eines Tiefenbildes mit einer Auflösung von 640x480 Pixeln
        msg.height = 480
        msg.width = 640
        msg.encoding = '16UC1' # 16-Bit unsigned int, 1 Kanal (Standard für Tiefe)
        msg.is_bigendian = 0
        msg.step = msg.width * 2 # 2 Bytes pro Pixel (16 Bit)

        # Generiere zufällige Tiefenwerte zwischen 500mm (0.5m) und 3000mm (3m)
        fake_depth_data = np.random.randint(500, 3000, (480, 640), dtype=np.uint16)
        msg.data = fake_depth_data.tobytes()

        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = FakeRealSense()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()