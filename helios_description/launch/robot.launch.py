from launch import LaunchDescription
from launch_ros.actions import Node 


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

    
        
    return LaunchDescription([
        twist2pwm,
        diff_tf,
        fkenc,
    ])