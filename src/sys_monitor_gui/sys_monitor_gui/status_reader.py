"""本机状态采集。

这个模块只负责读取数据，不依赖 ROS，便于单独测试。
"""

import socket

import psutil


def prime_cpu_percent():
    """预热 psutil 的 CPU 使用率。

    psutil.cpu_percent() 第一次调用没有参考值，只会返回 0.0，
    所以在开始周期性读取之前先调用一次。
    """
    psutil.cpu_percent()


def read_status():
    """读取一次本机状态。

    返回的字典键与 SystemStatus 消息字段一一对应。
    网络收发为开机以来的累计字节数。
    """
    memory = psutil.virtual_memory()
    net = psutil.net_io_counters()
    return {
        'hostname': socket.gethostname(),
        'cpu_percent': float(psutil.cpu_percent()),
        'memory_percent': float(memory.percent),
        'memory_total_bytes': int(memory.total),
        'memory_available_bytes': int(memory.available),
        'net_bytes_recv': int(net.bytes_recv),
        'net_bytes_sent': int(net.bytes_sent),
    }
