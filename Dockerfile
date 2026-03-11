# root file system
FROM ubuntu:24.04 

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    locales curl wget gnupg2 lsb-release software-properties-common build-essential git btop neofetch nano\
    && locale-gen en_US en_US.UTF-8

    #encodeing for the programe drunnign inside 
ENV LANG=en_US.UTF-8
ENV LC_ALL=en_US.UTF-8

RUN curl -sSL https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | apt-key add -
RUN echo "deb [arch=$(dpkg --print-architecture)] http://packages.ros.org/ros2/ubuntu \
    $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros2.list
    
RUN apt update && apt install -y ros-jazzy-desktop
RUN apt install -y python3-colcon-common-extensions ros-dev-tools
RUN apt install -y ros-jazzy-xacro ros-jazzy-joint-state-publisher-gui

RUN curl -sSL https://packages.osrfoundation.org/gazebo.gpg | apt-key add -
RUN echo "deb http://packages.osrfoundation.org/gazebo/ubuntu \
    $(lsb_release -cs) main" > /etc/apt/sources.list.d/gazebo-latest.list

# Add Gazebo Harmonic APT repo + key + install
RUN apt-get update && apt-get install -y curl gnupg lsb-release && \
    curl -fsSL https://packages.osrfoundation.org/gazebo.gpg -o /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg && \
    echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] https://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" \
    > /etc/apt/sources.list.d/gazebo-stable.list && \
    apt-get update && \
    apt-get install -y gz-harmonic && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y \
    ros-jazzy-ros-gz-sim \
    ros-jazzy-ros-gz-bridge && \
    apt-get clean && rm -rf /var/lib/apt/lists/*


    
SHELL ["/bin/bash", "-c"]
RUN echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc