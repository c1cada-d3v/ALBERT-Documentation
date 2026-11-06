import rclpy
from rclpy.node import Node
import serial
from std_msgs.msg import String

# This node is only for initializing communication with the ESP32
class Esp32_Rpi(Node):

  def __init__(self):
    super().__init__('esp32_rpi')

    self.esp32_comm_publisher = self.create_publisher(String, 'esp32_status', 10)
    self.get_logger().info('RPI-ESP: Searching...')
    
    self.connected = False
    
    try:
        self.ser = serial.Serial('/dev/tty0', 115200, timeout = 1)
    except serial.SerialException as e:
        self.get_logger().error(f'Failed to open serial port: {e}')
        self.ser = None

    self.timer = self.create_timer(1.0, self.check_handshake_callback)

  def check_handshake_callback(self):
    if self.ser is None or self.connected:
        return

    try:
        initcomms = self.ser.read(1)
        if initcomms == b'1':
        # Test value for the ESP32 to recieve back
            initvalue = 1
            print(f"RPI-ESP: Initializing with value {initvalue}")
            self.ser.write(f'{initvalue:.2f}\n'.encode('utf-8'))

            msg = String()
            msg.data = 'connected'
            self.esp32_comm_publisher.publish(msg)
            self.get_logger().info('RPI-ESP: Connection established!')
            self.connected = True

        else:
        # Handshake unsuccessful
            self.get_logger().warn('RPI-ESP: Connection failed!')
            
    except serial.SerialException:
        self.get_logger().error('Serial communication error occurred.')

def main(args=None):
  rclpy.init(args=args)
  node = Esp32_Rpi()
  try:
      rclpy.spin(node)
  except KeyboardInterrupt:
      pass
  finally:
      if node.ser and node.ser.is_open:
          node.ser.close()
      rclpy.shutdown()

if __name__ == '__main__':
  main()
