# ros2-system-monitor

在 **Ubuntu 22.04 + ROS 2 Humble** 上运行的本机实时状态监看，全部用 Python 编写，共两个包。

| 包 | 构建类型 | 作用 |
|---|---|---|
| `sys_monitor_interfaces` | `ament_cmake` | 只定义消息接口 `SystemStatus`，不含任何逻辑 |
| `sys_monitor_gui` | `ament_python` | 采集本机状态并发布，用 PyQt5 小窗口显示 |

## 目录结构

```
ros2-system-monitor/                 ← colcon 工作区根目录
├── LICENSE
├── README.md
├── PUSH_TO_GITHUB.md                ← 建库 + 推送命令清单
├── .gitignore
└── src/
    ├── sys_monitor_interfaces/
    │   ├── CMakeLists.txt
    │   ├── package.xml
    │   └── msg/SystemStatus.msg     ← 唯一的消息定义
    └── sys_monitor_gui/
        ├── package.xml
        ├── setup.py
        ├── setup.cfg
        ├── resource/sys_monitor_gui
        ├── launch/system_monitor.launch.py
        └── sys_monitor_gui/
            ├── __init__.py
            ├── status_reader.py     ← 读 psutil，不依赖 ROS
            ├── status_publisher.py  ← 采集节点：发布 system_status
            └── status_gui.py        ← 显示节点：PyQt5 窗口
```

## 数据流

```
psutil / socket
      │  每秒一次
      ▼
status_publisher 节点  ──发布──▶  话题 /system_status  ──订阅──▶  status_gui 节点（PyQt5 窗口）
   (SystemStatus)                      (SystemStatus)
```

## 依赖安装（Ubuntu 22.04 / Humble）

```bash
sudo apt update
sudo apt install -y python3-psutil python3-pyqt5
```

`ros-humble-desktop` 已包含本包用到的 `rclpy`、`std_msgs`、`launch`、`launch_ros`。
如果只装了 `ros-humble-ros-base`，还需要补 `launch_ros`。

## 编译

本仓库的根目录就是 colcon 工作区根目录（内部含 `src/`）：

```bash
cd ros2-system-monitor
colcon build --symlink-install
source install/setup.bash
```

## 运行

一条命令同时启动采集节点和窗口：

```bash
ros2 launch sys_monitor_gui system_monitor.launch.py
```

也可以分开启动（两个终端，各自先 `source install/setup.bash`）：

```bash
# 终端 1：采集并发布
ros2 run sys_monitor_gui status_publisher

# 终端 2：打开显示窗口
ros2 run sys_monitor_gui status_gui
```

## 在 WSL 里运行（Ubuntu 22.04 on WSL2）

WSL2 上可以正常跑（Windows 11 自带 WSLg，PyQt5 窗口直接显示，不需要额外装 X server），但下面几件事必须先做对，否则症状很迷惑人。

### 1. 项目要放在 Linux 自己的磁盘里

WSL 能直接看到 Windows 盘，但**不要在 `/mnt/c`、共享文件夹或 U 盘里 `colcon build`**：这些文件系统上创建符号链接会失败，`--symlink-install` 直接报错，而且速度慢一个数量级。先复制到家目录：

```bash
mkdir -p ~/ros2_ws/src
cp -r /mnt/c/Users/<你的Windows用户名>/.../ros2-system-monitor ~/ros2_ws/src/
```

### 2. 装中文字体，否则窗口是一整片空白

Qt 找不到任何可用字体时**不会报错**，而是把所有文字画成空白——窗口正常弹出、里面什么都没有，很容易误判成"程序没工作"。窗口里的标题和标签都是中文，所以这一步必做：

```bash
sudo apt install -y fonts-noto-cjk fonts-dejavu-core
fc-cache -fv
fc-list :lang=zh | wc -l        # 应大于 0
```

### 3. 每个终端都要 source 工作区

`ros2 run` / `ros2 launch` 报 `Package 'sys_monitor_gui' not found`，最常见的原因就是那个终端没 source 工作区（新开的终端不会自动 source）。写进 `~/.bashrc` 一劳永逸，注意这行必须在 `source /opt/ros/humble/setup.bash` **之后**：

```bash
echo 'source ~/ros2_ws/src/ros2-system-monitor/install/setup.bash' >> ~/.bashrc
```

`ros2 topic echo` / `ros2 topic hz` 属于基础工具，不需要 source 工作区。

### 4. 窗口显示的是 WSL 自己的资源

WSL2 是一台独立虚拟机，`free -h`、`nproc` 看到的是分给它的 CPU 和内存（默认约为 Windows 主机的一半）。所以窗口里的 CPU、内存、网卡都是 **WSL 虚拟机的**，不是 Windows 主机的。要监看 Windows 主机本身，得在 Windows 侧另跑一个采集程序。

### 5. 节点之间互相看不见时的排查

`ros2 topic hz` 报 `does not appear to be published yet`、或 `ros2 node list` 为空时，先排除 ROS 2 daemon 的假象，再用官方 demo 判断是环境问题还是本项目问题：

```bash
ros2 daemon stop
ros2 node list --no-daemon                    # 绕开 daemon 直接查

# 另一个终端：官方 demo，能通说明 ROS 2 本身没问题
ros2 run demo_nodes_cpp talker
ros2 topic echo /chatter
```

如果 demo 同样看不见，就是 WSL 里的 DDS 发现问题。注意 `ROS_LOCALHOST_ONLY`、`ROS_AUTOMATIC_DISCOVERY_RANGE`、`RMW_IMPLEMENTATION` 这些变量**只在设置它们的那个终端里生效**，一端设了另一端没设，就正好互相发现不了；要用就让所有终端一致（写进 `~/.bashrc`），改完关掉所有终端重开——环境变量只对之后启动的进程生效：

```bash
echo 'export ROS_LOCALHOST_ONLY=1' >> ~/.bashrc    # 只在本机通信；本项目两端同机，无副作用

# 或者换 DDS 实现（Fast DDS 在 WSL 上偶发多播问题）
sudo apt install -y ros-humble-rmw-cyclonedds-cpp
echo 'export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp' >> ~/.bashrc
```

### 6. 国内网络安装 ROS 2 的注意点

ROS 2 官方文档里下载 GPG key 用的是 `raw.githubusercontent.com`，国内常常连不通，可以换清华镜像（密钥指纹与官方一致：`C1CF6E31E6BADE8868B172B4F42ED6FBAB17C654`）：

```bash
sudo curl -sSL https://mirrors.tuna.tsinghua.edu.cn/rosdistro/ros.key \
  -o /usr/share/keyrings/ros-archive-keyring.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] https://mirrors.tuna.tsinghua.edu.cn/ros2/ubuntu jammy main" \
  | sudo tee /etc/apt/sources.list.d/ros2.list > /dev/null
```

这个 `ros.key` 是二进制格式，**直接下载**即可，不要再加 `gpg --dearmor`。

## 自检命令

```bash
ros2 interface show sys_monitor_interfaces/msg/SystemStatus   # 看消息定义
ros2 node list                                               # system_status_publisher / system_status_gui
ros2 topic list                                              # /system_status
ros2 topic echo /system_status                               # 看每条数据
ros2 topic hz /system_status                                 # 应接近 1 Hz
```

## 消息内容

`sys_monitor_interfaces/msg/SystemStatus.msg`

| 字段 | 类型 | 含义 |
|---|---|---|
| `header` | `std_msgs/Header` | 记录时间在 `header.stamp` |
| `hostname` | `string` | 主机名 |
| `cpu_percent` | `float32` | CPU 使用率（0–100） |
| `memory_percent` | `float32` | 内存使用率（0–100） |
| `memory_total_bytes` | `uint64` | 内存总大小（字节） |
| `memory_available_bytes` | `uint64` | 剩余可用内存（字节） |
| `net_bytes_recv` | `uint64` | 开机以来累计接收字节数 |
| `net_bytes_sent` | `uint64` | 开机以来累计发送字节数 |

## 采集周期

默认 1 秒一次，可以调：

```bash
ros2 run sys_monitor_gui status_publisher --ros-args -p publish_period:=0.5
```

## 作者与许可

作者：蔡俊杰（3510173849@qq.com）。许可：Apache-2.0，见 `LICENSE`。

## 范围说明

按需求刻意**不做**的内容：不采集远程主机、不做多机汇总、不做数据落盘/历史曲线、不做告警、不做阈值配置、不做进程级监控、不计算网络速率。
`hostname` 字段已保留在消息里，将来要扩成多机也不用改接口。
