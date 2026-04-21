# Ackermann Mobile Manipulator - ROS 2 Midterm Project

## 1. Mô tả
Dự án mô phỏng một hệ thống robot di động kết hợp tay máy (Mobile Manipulator) trên môi trường ROS 2 Humble. Robot sử dụng cơ cấu lái Ackermann (Car-like) cho khung gầm và tích hợp tay máy 2 bậc tự do dạng xoay - xoay (R-R):
- Hệ truyền động: Cơ cấu lái Ackermann thực tế với 2 bánh trước dẫn hướng và 2 bánh sau truyền động lực.
- Tay máy (2-DOF R-R):
  - Khớp 1: Xoay ngang (Swing) quanh trục Z thẳng đứng.
  - Khớp 2: Xoay đứng (Pitch) quanh trục Y để nâng/hạ cánh tay.
- Hệ thống cảm biến:
  - LiDAR: Quét 360 độ phục vụ bài toán tránh vật cản.
  - IMU: Được gắn đặc biệt tại đầu tay máy (link2) để đo trực tiếp độ ổn định của khâu thao tác cuối.

## 2. Cấu trúc packagePlaintext.
```
├── 📦 base_controller              # Package chứa các node điều khiển (Python)
│   ├── 📁 config                   # Chứa cấu hình bộ điều khiển (arm_controller.yaml)
│   ├── 📄 teleop_ackermann.py      # Node điều khiển xe (Hỗ trợ phanh ABS & tự trả lái)
│   └── 📄 teleop_arm.py            # Node điều khiển tay máy (Khóa giới hạn phần cứng)
│
└── 📦 robot_description            # Package chứa mô hình và mô phỏng (Xacro/URDF)
    ├── 📄 CMakeLists.txt           # File cấu hình biên dịch CMake
    ├── 📄 package.xml              # Định nghĩa dependencies và plugins
    ├── 📁 mesh                     # Chứa các file 3D (.stl) của bánh xe và cánh tay
    ├── 📁 urdf                     # Kiến trúc URDF Module hóa (Xacro)
    │   ├── 📄 robot.urdf.xacro     # File tổng hợp (Main)
    │   ├── 📄 base.xacro           # Module khung gầm Ackermann
    │   ├── 📄 arm.xacro            # Module tay máy R-R & ros2_control
    │   └── 📄 sensors.xacro        # Module LiDAR & IMU
    ├── 📁 launch                   # Các tệp khởi chạy hệ thống
    │   └── 🚀 sim.launch.py        # Khởi chạy Gazebo + RViz2 + Controller Spawners
    └── 📁 rviz                     # Cấu hình trực quan hóa
        └── 📄 config.rviz          # File làm sẵn cấu hình RViz2
```
## 3. Môi trường
- Hệ điều hành: Ubuntu 22.04 LTS
- Phiên bản ROS: ROS 2 Humble
- Trình mô phỏng: Gazebo Classic
- Giao diện trực quan: RViz2

## 4. Cài đặt
Yêu cầu đã cài đặt sẵn ROS 2 Humble.
```
# 1. Tạo workspace và tải mã nguồn
mkdir -p ~/giua_ky_ws/src
cd ~/giua_ky_ws/src
git clone https://github.com/QuanJB/giua_ky_ros.git
cd ..

# 2. Cài đặt công cụ quản lý thư viện rosdep
sudo apt update
sudo apt install python3-rosdep
sudo rosdep init
rosdep update

# 3. Tự động cài đặt toàn bộ dependencies của dự án
rosdep install --from-paths src -y --ignore-src

# 4. Biên dịch hệ thống
colcon build --symlink-install
source install/setup.bash
```
## 5. Cách chạy
Mở các terminal riêng biệt và nạp môi trường (```source install/setup.bash```) trước khi thực hiện:
- Khởi chạy mô phỏng (Gazebo + RViz2 + Controllers):
```
ros2 launch robot_description sim.launch.py
```
- Điều khiển xe Ackermann:
```
ros2 run base_controller teleop_ackermann
```
- Điều khiển tay máy:
```
ros2 run base_controller teleop_arm
```

## 6. Ghi chú kỹ thuật
- Dự án áp dụng phương pháp thiết kế Code-First bằng Xacro, cho phép tham số hóa toàn bộ kích thước robot.
- Bộ điều khiển lái Ackermann đã được tinh chỉnh PID ($K_p=100, K_d=20$) để loại bỏ hiện tượng rung bánh xe trong Gazebo.
- Sử dụng lệnh colcon build --symlink-install giúp cập nhật ngay lập tức các thay đổi trong file Xacro hoặc Script Python mà không cần biên dịch lại nhiều lần.
