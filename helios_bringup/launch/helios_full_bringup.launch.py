#!/usr/bin/python3
import os
import launch, launch_ros
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_prefix
from launch_ros.actions import Node


def generate_launch_description():

  pkg_helios_gazebo = get_package_share_directory('helios_gazebo')
  pkg_helios_description = get_package_share_directory('helios_description')

  gazebo = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(pkg_helios_gazebo, 'launch', 'gazebo.launch.py'),
    )
  ) 
  
  rviz2 = IncludeLaunchDescription(
    PythonLaunchDescriptionSource(
      os.path.join(pkg_helios_description, 'launch', 'display.launch.py'),
    )
  )

  return LaunchDescription([
    gazebo,
    rviz2
  ])
  