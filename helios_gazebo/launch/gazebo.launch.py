import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    AppendEnvironmentVariable,
    DeclareLaunchArgument,
    ExecuteProcess,
    IncludeLaunchDescription,
    RegisterEventHandler,
    TimerAction
)
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch_ros.actions import Node
from os.path import join
import xacro


def generate_launch_description():

    # Package Directories
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')
    pkg_ros_gz_rbot = get_package_share_directory('helios_description')
    pkg_gz = get_package_share_directory('helios_gazebo')

    # Parse robot description from xacro
    robot_description_file = os.path.join(pkg_ros_gz_rbot, 'urdf', 'helios_description.xacro')
    ros_gz_bridge_config = os.path.join(pkg_ros_gz_rbot, 'config', 'ros_gz_bridge_gazebo.yaml')

    robot_description_config = xacro.process_file(robot_description_file)
    robot_description = {'robot_description': robot_description_config.toxml()}

    world_file = os.path.join(pkg_gz, 'worlds', 'test_world.sdf')

    # Launch arguments
    declare_load_controllers_cmd = DeclareLaunchArgument(
        name='load_controllers',
        default_value='true',
        description='Flag to enable loading of ROS 2 controllers'
    )
    load_controllers = LaunchConfiguration('load_controllers')

    # Environment
    gazebo_model_path = AppendEnvironmentVariable(
        'GZ_SIM_RESOURCE_PATH',
        os.path.join(pkg_gz, 'models')
    )

    # Robot State Publisher
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[robot_description],
    )

    # Gazebo Sim
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(join(pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py')),
        launch_arguments={
            'gz_args': '-r -v 4 empty.sdf'
            # 'gz_args': f'-r -v 4 {world_file}'
        }.items()
    )

    # Spawn Robot
    spawn = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', '/robot_description',
            '-name', 'helios_description',
            '-allow_renaming', 'true',
            '-z', '0.08',
            '-x', '0.0',
            '-y', '0.0',
            '-Y', '0.0'
        ],
        output='screen',
    )

    # ROS-Gazebo Bridge
    start_gazebo_ros_bridge_cmd = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': ros_gz_bridge_config,
        }],
        output='screen'
    )

    # Controllers — JSB first, then mecanum on JSB exit
    start_joint_state_broadcaster_cmd = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'joint_state_broadcaster'],
        output='screen'
    )

    start_mecanum_drive_controller_cmd = ExecuteProcess(
        cmd=['ros2', 'control', 'load_controller', '--set-state', 'active',
             'mecanum_drive_controller'],
        output='screen'
    )

    # Wait for spawn to finish, then load JSB after a short delay
    load_controllers_cmd = TimerAction(
        period=5.0,
        actions=[start_joint_state_broadcaster_cmd]
    )

    # Load mecanum controller after JSB finishes loading
    load_mecanum_on_jsb_exit = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=start_joint_state_broadcaster_cmd,
            on_exit=[start_mecanum_drive_controller_cmd]
        )
    )

    return LaunchDescription([
        declare_load_controllers_cmd,

        gazebo_model_path,
        gazebo,
        robot_state_publisher,
        spawn,
        start_gazebo_ros_bridge_cmd,

        load_controllers_cmd,
        load_mecanum_on_jsb_exit,
    ])