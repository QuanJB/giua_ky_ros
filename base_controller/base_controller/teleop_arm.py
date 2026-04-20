import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray
import sys, select, termios, tty

class ArmTeleop(Node):
    def __init__(self):
        super().__init__('arm_teleop')
        # Gửi dữ liệu vào topic điều khiển của ros2_control
        self.publisher_ = self.create_publisher(Float64MultiArray, '/arm_controller/commands', 10)
        self.angle1 = 0.0 # Góc joint1 (Pan)
        self.angle2 = 0.0 # Góc joint2 (Tilt)
        self.step = 0.05  # Tốc độ xoay mỗi lần bấm
        
        self.get_logger().info("ĐÃ KẾT NỐI TAY MÁY!")
        self.get_logger().info("Dùng phím J/L để xoay Trái/Phải (Joint1)")
        self.get_logger().info("Dùng phím I/K để gật Lên/Xuống (Joint2)")
        self.get_logger().info("Bấm 'q' để thoát.")

    def read_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        return key

    def run(self):
        settings = termios.tcgetattr(sys.stdin)
        try:
            while rclpy.ok():
                key = self.read_key()
                
                # Logic map phím I J K L
                if key == 'j' or key == 'J':
                    self.angle1 += self.step
                elif key == 'l' or key == 'L':
                    self.angle1 -= self.step
                elif key == 'i' or key == 'I':
                    self.angle2 += self.step
                elif key == 'k' or key == 'K':
                    self.angle2 -= self.step
                elif key == 'q' or key == 'Q':
                    break

                # Giới hạn góc quay theo đúng URDF ông đã định nghĩa
                self.angle1 = max(-3.14, min(3.14, self.angle1))
                self.angle2 = max(-1.57, min(1.57, self.angle2))

                # Đóng gói và gửi cho Gazebo
                msg = Float64MultiArray()
                msg.data = [self.angle1, self.angle2]
                self.publisher_.publish(msg)
                
                print(f"\r[ARM] Đế (J/L): {self.angle1:5.2f} rad | Trục (I/K): {self.angle2:5.2f} rad    ", end="")
        finally:
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

def main(args=None):
    rclpy.init(args=args)
    node = ArmTeleop()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()