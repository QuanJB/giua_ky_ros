#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty

msg = """
ĐANG ĐIỀU KHIỂN XE ACKERMANN (BẢN PRO)
---------------------------
Mũi tên LÊN    : Đạp ga Tiến
Mũi tên XUỐNG  : Đạp ga Lùi
Mũi tên TRÁI   : Đánh lái sang Trái
Mũi tên PHẢI   : Đánh lái sang Phải
Phím SPACE     : Phanh gấp cứng tay
Phím 'q'       : Thoát
*(Thả tay ra xe sẽ tự rà phanh và trả thẳng lái)*
---------------------------
"""

class TeleopAckermann(Node):
    def __init__(self):
        super().__init__('teleop_ackermann')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        
        self.speed = 0.0          
        self.steering_angle = 0.0 
        
        self.MAX_SPEED = 0.4
        self.MAX_STEER = 0.5      

        self.get_logger().info(msg)

    def get_key(self, settings):
        tty.setraw(sys.stdin.fileno())
        # TÍNH NĂNG MỚI: Chỉ chờ phím trong 0.1 giây. Nếu không ai bấm, bỏ qua đi tiếp!
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        
        if rlist:
            key = sys.stdin.read(1)
            if key == '\x1b':
                key += sys.stdin.read(2)
        else:
            key = '' # Không có phím nào được bấm
            
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key

    def run(self):
        settings = termios.tcgetattr(sys.stdin)
        twist = Twist()

        try:
            while rclpy.ok():
                key = self.get_key(settings)

                if key == '\x1b[A':   # Lên
                    self.speed = min(self.MAX_SPEED, self.speed + 0.02) # Tăng mượt hơn
                elif key == '\x1b[B': # Xuống
                    self.speed = max(-self.MAX_SPEED, self.speed - 0.02)
                elif key == '\x1b[D': # Trái
                    self.steering_angle = min(self.MAX_STEER, self.steering_angle + 0.15)
                elif key == '\x1b[C': # Phải
                    self.steering_angle = max(-self.MAX_STEER, self.steering_angle - 0.15)
                elif key == ' ' or key == 's' or key == 'S': # Hệ thống Phanh
                    # BÍ KÍP 1: Chế độ phanh ABS (Phanh dịu)
                    # Thay vì chốt cứng 0.0, ta triệt tiêu 70% động năng mỗi nhịp (0.1 giây)
                    self.speed *= 0.85 
                    if abs(self.speed) < 0.05: 
                        self.speed = 0.0
                    
                    # BÍ KÍP 2: TUYỆT ĐỐI KHÔNG GIẬT VÔ LĂNG KHI PHANH GẤP
                    # (Đã XÓA dòng self.steering_angle = 0.0 ở đây)
                    # Cứ để vô lăng giữ nguyên góc cua, hoặc để bộ "Quán tính" ở dưới tự trả lái dần dần
                    
                    print(f"\r[PHANH ABS] Đang hãm tốc độ...             ", end="")
                elif key == 'q':      # Thoát
                    break
                else:                 
                    # TÍNH NĂNG QUÁN TÍNH: Nếu không ấn phím nào, tự động giảm dần về 0
                    self.speed *= 0.85          # Rà phanh từ từ (Giảm 15% mỗi nhịp)
                    self.steering_angle *= 0.80 # Vô lăng bật ngược về giữa nhanh hơn
                    
                    # Cắt đuôi số thập phân nhỏ để xe dừng hẳn
                    if abs(self.speed) < 0.02: self.speed = 0.0
                    if abs(self.steering_angle) < 0.02: self.steering_angle = 0.0

                # Gửi lệnh
                twist.linear.x = self.speed
                twist.angular.z = self.steering_angle
                self.publisher_.publish(twist)
                
                print(f"\rTốc độ: {self.speed:5.2f} m/s | Góc lái: {self.steering_angle:5.2f} rad   ", end="")

        except Exception as e:
            print(e)
        finally:
            twist.linear.x = 0.0
            twist.angular.z = 0.0
            self.publisher_.publish(twist)
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)

def main(args=None):
    rclpy.init(args=args)
    node = TeleopAckermann()
    node.run()
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()