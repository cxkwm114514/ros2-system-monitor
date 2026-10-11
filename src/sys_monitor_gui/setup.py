import os
from glob import glob

from setuptools import setup

package_name = 'sys_monitor_gui'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='蔡俊杰',
    maintainer_email='3510173849@qq.com',
    description='Collect local machine status and display it in a PyQt5 window.',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'status_publisher = sys_monitor_gui.status_publisher:main',
            'status_gui = sys_monitor_gui.status_gui:main',
        ],
    },
)
