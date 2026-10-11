"""采集本机状态并按固定周期发布 SystemStatus 消息的节点。"""

import rclpy
from rclpy.node import Node

from sys_monitor_interfaces.msg import SystemStatus

from sys_monitor_gui.status_reader import prime_cpu_percent, read_status

DEFAULT_PUBLISH_PERIOD = 1.0


class SystemStatusPublisher(Node):
    """周期性发布本机实时状态。"""

    def __init__(self):
        super().__init__('system_status_publisher')

        self.declare_parameter('publish_period', DEFAULT_PUBLISH_PERIOD)
        self._publish_period = self.get_parameter('publish_period').value

        self._publisher = self.create_publisher(SystemStatus, 'system_status', 10)

        # 第一次读取 CPU 使用率没有参考值，先预热一次。
        prime_cpu_percent()

        self._timer = self.create_timer(self._publish_period, self._publish_status)

        self.get_logger().info(
            '系统状态采集已启动：话题 system_status，周期 %.2f 秒' % self._publish_period
        )

    def _publish_status(self):
        status = read_status()

        msg = SystemStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.hostname = status['hostname']
        msg.cpu_percent = status['cpu_percent']
        msg.memory_percent = status['memory_percent']
        msg.memory_total_bytes = status['memory_total_bytes']
        msg.memory_available_bytes = status['memory_available_bytes']
        msg.net_bytes_recv = status['net_bytes_recv']
        msg.net_bytes_sent = status['net_bytes_sent']

        self._publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SystemStatusPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
