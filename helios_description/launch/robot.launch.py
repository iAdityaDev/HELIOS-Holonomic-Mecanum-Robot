from launch import LaunchDescription
from launch_ros.actions import Node 
import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():

    twist2pwm = Node(
        package='helios_description',
        executable='twist_2_pwm',
        name='twist2pwm',
        output = 'screen',
        # namespace='',
    )

    diff_tf = Node(
        package='helios_description',
        executable='diff_tf',
        name='diff_tf',
        output = 'screen',
        # namespace='',
    )

    fkenc = Node(
        package='helios_description',
        executable='fkenc',
        name='fkenc',
        output = 'screen',
        # namespace='',
    )

    rviz_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('helios_description'),
                'launch',
                'display.launch.py'
            )
        )
    )

    
        
    return LaunchDescription([
        rviz_launch,
        twist2pwm,
        diff_tf,
        # fkenc,
    ])