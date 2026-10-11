"""用 PyQt5 小窗口显示本机实时状态的节点。"""

import sys
from datetime import datetime

import rclpy
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QFormLayout, QLabel, QWidget
from rclpy.node import Node

from sys_monitor_interfaces.msg import SystemStatus

WINDOW_TITLE = '本机状态监看'
WAITING_TEXT = '等待数据…'
SPIN_INTERVAL_MS = 50

_BYTE_UNITS = ('B', 'KB', 'MB', 'GB', 'TB', 'PB')


def format_bytes(num_bytes):
    """把字节数转成带单位的可读文本。"""
    value = float(num_bytes)
    for unit in _BYTE_UNITS:
        if value < 1024.0 or unit == _BYTE_UNITS[-1]:
            if unit == 'B':
                return '%d %s' % (int(value), unit)
            return '%.2f %s' % (value, unit)
        value /= 1024.0


def format_percent(value):
    """把百分比转成带单位的文本。"""
    return '%.2f %%' % value


def format_stamp(stamp):
    """把消息里的时间戳转成本地时间文本。"""
    if stamp.sec == 0 and stamp.nanosec == 0:
        return WAITING_TEXT
    seconds = stamp.sec + stamp.nanosec / 1e9
    return datetime.fromtimestamp(seconds).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]


class SystemStatusWindow(QWidget):
    """显示一条 SystemStatus 的小窗口。"""

    FIELDS = (
        ('time', '记录时间'),
        ('hostname', '主机名'),
        ('cpu_percent', 'CPU 使用率'),
        ('memory_percent', '内存使用率'),
        ('memory_total_bytes', '内存总大小'),
        ('memory_available_bytes', '剩余内存'),
        ('net_bytes_recv', '网络接收（累计）'),
        ('net_bytes_sent', '网络发送（累计）'),
    )

    def __init__(self):
        super().__init__()

        self.setWindowTitle(WINDOW_TITLE)
        self._labels = {}

        layout = QFormLayout(self)
        for key, title in self.FIELDS:
            label = QLabel(WAITING_TEXT)
            self._labels[key] = label
            layout.addRow('%s：' % title, label)

    def update_status(self, msg):
        """按收到的消息刷新窗口上的每一个字段。"""
        texts = {
            'time': format_stamp(msg.header.stamp),
            'hostname': msg.hostname,
            'cpu_percent': format_percent(msg.cpu_percent),
            'memory_percent': format_percent(msg.memory_percent),
            'memory_total_bytes': format_bytes(msg.memory_total_bytes),
            'memory_available_bytes': format_bytes(msg.memory_available_bytes),
            'net_bytes_recv': format_bytes(msg.net_bytes_recv),
            'net_bytes_sent': format_bytes(msg.net_bytes_sent),
        }
        for key, text in texts.items():
            self._labels[key].setText(text)

    def label_text(self, key):
        """读取某个字段当前显示的文本（供测试使用）。"""
        return self._labels[key].text()


class SystemStatusGuiNode(Node):
    """订阅 system_status，并把每条消息交给窗口显示。"""

    def __init__(self, window):
        super().__init__('system_status_gui')
        self._window = window
        self.create_subscription(SystemStatus, 'system_status', self._on_status, 10)

    def _on_status(self, msg):
        self._window.update_status(msg)


def main(args=None):
    rclpy.init(args=args)

    # 只把程序名交给 Qt，避免 ROS 的命令行参数干扰窗口。
    app = QApplication([sys.argv[0]])
    window = SystemStatusWindow()
    node = SystemStatusGuiNode(window)

    # Qt 事件循环自己跑，ROS 消息用定时器代为处理。
    spin_timer = QTimer()
    spin_timer.timeout.connect(lambda: rclpy.spin_once(node, timeout_sec=0.0))
    spin_timer.start(SPIN_INTERVAL_MS)

    window.show()
    try:
        exit_code = app.exec_()
    finally:
        spin_timer.stop()
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

    return exit_code


if __name__ == '__main__':
    sys.exit(main())
