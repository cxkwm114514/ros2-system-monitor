"""一条命令同时启动状态采集节点和显示窗口。"""

from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='sys_monitor_gui',
            executable='status_publisher',
            name='system_status_publisher',
            output='screen',
        ),
        Node(
            package='sys_monitor_gui',
            executable='status_gui',
            name='system_status_gui',
            output='screen',
        ),
    ])
