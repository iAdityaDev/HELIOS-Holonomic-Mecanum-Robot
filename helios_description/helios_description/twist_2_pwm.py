#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32,Int64
from geometry_msgs.msg import Twist
import math
# import ik_solver as inverse_kine
# import ik_solver as ik_solver

class Helios_IK(Node):
    def __init__(self):
        super().__init__('Teleop')

        self.get_logger().info('Teleop node for CHipta is now alive')

        self.twist_subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self.twist_callback,
            10
        )
        # print(self.twist_subscription)

        self.pwm_pub = self.create_publisher(Int64, '/pwm', 10)
        self.pwm = Int64()

        # all the values are in the m 
        self.motor_rpm = 350
        self.wheel_diameter = 0.06
        self.wheel_separation = 0.156
        self.length_offset = 0.078
        self.breadth_offset = 0.065 
        self.max_pwm_val = 255 
        self.min_pwm_val = -255
        self.wheel_radius = self.wheel_diameter / 2
        self.inverse_wheel_radius = 1.0 / self.wheel_radius
        # print(self.inverse_wheel_radius)
        self.circumference = math.pi * self.wheel_diameter
        self.max_speed = (self.circumference * self.motor_rpm) / 60
        self.max_angular = self.max_speed/(self.wheel_diameter/2)
        # print(f"max speed{self.max_speed}")
        # print(f"max speed{self.max_angular}")
        # print('in the end of the init')

        # self.ik = ik_solver(self,self.length_offset, self.breadth_offset, self.wheel_radius)

    def solve(self, vx, vy, vz):
        ##front left
        self.omega_front_left = self.inverse_wheel_radius * (vx - vy - vz * (self.length_offset + self.breadth_offset))
        ##front right
        self.omega_front_right = self.inverse_wheel_radius * (vx + vy + vz*(self.length_offset + self.breadth_offset))
        ##back left
        self.omega_back_left = self.inverse_wheel_radius * (vx + vy - vz*(self.length_offset + self.breadth_offset))
        ##back right
        self.omega_back_right = self.inverse_wheel_radius * (vx - vy + vz*(self.length_offset + self.breadth_offset))
        
        return (self.omega_front_left, self.omega_front_right, self.omega_back_left, self.omega_back_right)

    def stop(self):
        self.pwm.data = 0
        self.pwm_pub.publish(self.pwm)

    # def get_pwm(self,speed):
    #     speed = int(max(min((speed / self.max_speed) * self.max_pwm_val, self.max_pwm_val), self.min_pwm_val))
    #     return speed

    def get_pwm(self,omega):
        rpm = omega * (60 / (2 * math.pi)) # omega/60/2pi
        if rpm>350:
            rpm = 350
        # print(f'rpm/rpm/rpm/rpm{rpm}')
        normal = rpm/self.motor_rpm
        # print(f'normal/normal/normal{normal}')
        pwm = 255 + (normal*255)
        return pwm
    
    def twist_callback(self, data):
        print("callback me aagya")
        linear_vel_x = data.linear.x  
        linear_vel_y = data.linear.y  # Linear Velocity of Robot
        angular_vel = data.angular.z  

        self.omega_front_left, self.omega_front_right, self.omega_back_left, self.omega_back_right = self.solve(linear_vel_x,linear_vel_y,angular_vel)
        print(f'omega_front_left   {self.omega_front_left}')
        print(f'omega_front_right   {self.omega_front_right}')
        print(f'omega_back_left   {self.omega_back_left}')
        print(f'omega_back_right   {self.omega_back_right}')

        self.front_left_pwm = int(self.get_pwm(self.omega_front_left))
        self.front_right_pwm = int(self.get_pwm(self.omega_front_right))
        self.back_left_pwm = int(self.get_pwm(self.omega_back_left))
        self.back_right_pwm = int(self.get_pwm(self.omega_back_right))

        # self.v_front_left_pwm = max(self.min_pwm_val, min(self.max_pwm_val, self.v_front_left_pwm))
        # self.v_front_right_pwm = max(self.min_pwm_val, min(self.max_pwm_val, self.v_front_right_pwm))
        # self.v_back_left_pwm = max(self.min_pwm_val, min(self.max_pwm_val, self.v_back_left_pwm))
        # self.v_back_right_pwm = max(self.min_pwm_val, min(self.max_pwm_val, self.v_back_right_pwm))
        
        # new_max = 90

        # mflp = new_max * (self.v_front_left_pwm / 255) 
        # mfrp = new_max * (self.v_front_right_pwm / 255)
        # mblp = new_max * (self.v_back_left_pwm / 255)
        # mbrp = new_max * (self.v_back_right_pwm / 255)
        # print(mflp)
        # print(mfrp)


        print(self.front_left_pwm)
        print(self.front_right_pwm)
        print(self.back_left_pwm)
        print(self.back_right_pwm)

        self.pwm.data = int((self.front_left_pwm)*1000*1000*1000+(self.front_right_pwm)*1000*1000+(self.back_left_pwm)*1000+self.back_right_pwm)
        # self.pwm.data = int((mflp)*100*100*100+(mfrp)*100*100+(mblp)*100+mbrp)
        print(self.pwm.data)
        # print(self.pwm[1][1])
    
        self.pwm_pub.publish(self.pwm)


def main(args=None):
    rclpy.init(args=args)
    node = Helios_IK()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()