import rclpy 
from rclpy.node import Node 
from geometry_msgs.msg import Quaternion, Twist,TransformStamped # quater orien in 3d space odom and tf  # tranfprm pub tf transforms base_link -> odom
from std_msgs.msg import Int32,Int64
from nav_msgs.msg import Odometry # contains x,y,z ,orien(quaternion), linear and angular vels
from tf2_ros import TransformBroadcaster
import numpy as np
import math
from math import sin , cos , pi

class DiffTF(Node):
    def __init__(self):
        super().__init__('diff_tf')
        self.get_logger().info('diff node is alive')

        self.create_subscription(Int64, "/fr_encoder_ticks", self.fr_wheel_callback, 10)
        self.create_subscription(Int64, "/fl_encoder_ticks", self.fl_wheel_callback, 10)
        self.create_subscription(Int64, "/rr_encoder_ticks", self.rr_wheel_callback, 10)
        self.create_subscription(Int64, "/rl_encoder_ticks", self.rl_wheel_callback, 10)
        self.odom_pub = self.create_publisher(Odometry, "/odom", 10)
        self.odom_broadcaster = TransformBroadcaster(self)

        self.rate_hz = self.declare_parameter("rate_hz", 30.0).value
        self.ticks_meter_fr = float(self.declare_parameter('ticks_meter_fr', 1857).value)  
        self.ticks_meter_fl = float(self.declare_parameter('ticks_meter_fl', 1857).value)  
        self.ticks_meter_rr = float(self.declare_parameter('ticks_meter_rr', 1857).value)  
        self.ticks_meter_rl = float(self.declare_parameter('ticks_meter_rl', 1857).value)

        self.encoder_min = int(self.declare_parameter('encoder_min', -9223372036854775808).value)
        self.encoder_max = int(self.declare_parameter('encoder_max',  9223372036854775807).value)
        self.encoder_low_wrap = self.declare_parameter('wheel_low_wrap', (
                self.encoder_max - self.encoder_min) * 0.3 + self.encoder_min).value
        self.encoder_high_wrap = self.declare_parameter('wheel_high_wrap', (
                self.encoder_max - self.encoder_min) * 0.7 + self.encoder_min).value
        self.base_frame_id = self.declare_parameter('base_frame_id','base_link').value
        self.odom_frame_id = self.declare_parameter('odom_frame_id','odom').value

        self.frmult = 0.0
        self.curr_fr_enc = None
        self.prev_fr_enc = None
        self.flmult = 0.0
        self.curr_fl_enc = None
        self.prev_fl_enc = None
        self.rrmult = 0.0
        self.curr_rr_enc = None
        self.prev_rr_enc = None
        self.rlmult = 0.0
        self.curr_rl_enc = None
        self.prev_rl_enc = None

        # meters 
        self.motor_rpm = 350
        self.wheel_diameter = 0.06
        self.wheel_radius = self.wheel_diameter / 2
        self.L = 0.156
        self.W = 0.130
        self.x = 0.0
        self.y = 0.0
        self.th = 0.0
        self.circumference = math.pi * self.wheel_diameter
        self.max_speed = (self.circumference * self.motor_rpm) / 60
        self.max_angular = self.max_speed/(self.wheel_diameter/2)

        self.last_time = 0.0
        self.create_timer(1.0 / self.rate_hz, self.update)

    def fr_wheel_callback(self,msg):
        enc = msg.data

        if self.prev_fr_enc is None:
            self.prev_fr_enc = enc
            self.curr_fr_enc = enc
            return
        
        #   self.get_logger().info(f"Left encoder ticks received: {enc}")
        if enc < self.encoder_low_wrap and self.prev_fr_enc > self.encoder_high_wrap:
            self.frmult = self.frmult + 1

        if enc > self.encoder_high_wrap and self.prev_fr_enc < self.encoder_low_wrap:
            self.frmult = self.frmult - 1

        self.curr_fr_enc = 1.0 * (enc + self.frmult * (self.encoder_max - self.encoder_min))


    def fl_wheel_callback(self,msg):
        enc = msg.data

        if self.prev_fl_enc is None:
            self.prev_fl_enc = enc
            self.curr_fl_enc = enc
            return
        
        #   self.get_logger().info(f"Left encoder ticks received: {enc}")
        if enc < self.encoder_low_wrap and self.prev_fl_enc > self.encoder_high_wrap:
            self.flmult = self.flmult + 1

        if enc > self.encoder_high_wrap and self.prev_fl_enc < self.encoder_low_wrap:
            self.flmult = self.flmult - 1

        self.curr_fl_enc = 1.0 * (enc + self.flmult * (self.encoder_max - self.encoder_min))

    def rr_wheel_callback(self,msg):
        enc = msg.data

        if self.prev_rr_enc is None:
            self.prev_rr_enc = enc
            self.curr_rr_enc = enc
            return
        
        #   self.get_logger().info(f"Left encoder ticks received: {enc}")
        if enc < self.encoder_low_wrap and self.prev_rr_enc > self.encoder_high_wrap:
            self.rrmult = self.rrmult + 1

        if enc > self.encoder_high_wrap and self.prev_rr_enc < self.encoder_low_wrap:
            self.rrmult = self.rrmult - 1

        self.curr_rr_enc = 1.0 * (enc + self.rrmult * (self.encoder_max - self.encoder_min))

    def rl_wheel_callback(self,msg):
        enc = msg.data

        if self.prev_rl_enc is None:
            self.prev_rl_enc = enc
            self.curr_rl_enc = enc
            return
        
        #   self.get_logger().info(f"Left encoder ticks received: {enc}")
        if enc < self.encoder_low_wrap and self.prev_rl_enc > self.encoder_high_wrap:
            self.rlmult = self.rlmult + 1

        if enc > self.encoder_high_wrap and self.prev_rl_enc < self.encoder_low_wrap:
            self.rlmult = self.rlmult - 1

        self.curr_rl_enc = 1.0 * (enc + self.rlmult * (self.encoder_max - self.encoder_min))

    def update(self):
        if None in [self.curr_fr_enc, self.curr_fl_enc, self.curr_rr_enc, self.curr_rl_enc]:
            return
        now = self.get_clock().now()
        if self.last_time == 0:
            self.last_time = now.nanoseconds
            return
        
        dt = (now.nanoseconds - self.last_time)/1e9
        if dt <= 0:
            return
        self.last_time = now.nanoseconds

        print(self.curr_fl_enc,self.prev_fl_enc)
        d_fr = (self.curr_fr_enc - self.prev_fr_enc) / self.ticks_meter_fr
        self.prev_fr_enc = self.curr_fr_enc
        d_fl = (self.curr_fl_enc - self.prev_fl_enc) / self.ticks_meter_fl
        self.prev_fl_enc = self.curr_fl_enc
        d_rr = (self.curr_rr_enc - self.prev_rr_enc) / self.ticks_meter_rr
        self.prev_rr_enc = self.curr_rr_enc
        d_rl = (self.curr_rl_enc - self.prev_rl_enc) / self.ticks_meter_rl
        self.prev_rl_enc = self.curr_rl_enc
        print(d_fr)

        v_fr = d_fr / dt
        v_fl = d_fl / dt
        v_rr = d_rr / dt
        v_rl = d_rl / dt

        vx = (self.wheel_radius/4) * (v_fl + v_fr + v_rl + v_rr)
        vy = (self.wheel_radius/4) * (-v_fl + v_fr + v_rl - v_rr)
        vth = (self.wheel_radius / (4 * (self.L + self.W))) * (-v_fl + v_fr - v_rl + v_rr)

        self.x += (vx * np.cos(self.th) - vy * np.sin(self.th)) * dt
        self.y += (vx * np.sin(self.th) + vy * np.cos(self.th)) * dt
        self.th += vth * dt
        print(self.x,self.y,self.th)

        quaternion = Quaternion()
        quaternion.x = 0.0
        quaternion.y = 0.0
        quaternion.z = sin(self.th / 2)
        quaternion.w = cos(self.th / 2)

        transform_stamped_msg = TransformStamped()
        transform_stamped_msg.header.stamp = now.to_msg()
        transform_stamped_msg.header.frame_id = self.odom_frame_id  # "odom"
        transform_stamped_msg.child_frame_id = self.base_frame_id   # "base_link"
        transform_stamped_msg.transform.translation.x = self.x
        transform_stamped_msg.transform.translation.y = self.y
        transform_stamped_msg.transform.translation.z = 0.0 
        transform_stamped_msg.transform.rotation.x = quaternion.x
        transform_stamped_msg.transform.rotation.y = quaternion.y
        transform_stamped_msg.transform.rotation.z = quaternion.z
        transform_stamped_msg.transform.rotation.w = quaternion.w

        self.odom_broadcaster.sendTransform(transform_stamped_msg)

        odom = Odometry()
        odom.header.stamp = now.to_msg()
        odom.header.frame_id = self.odom_frame_id
        odom.child_frame_id = self.base_frame_id
        odom.pose.pose.position.x = self.x
        odom.pose.pose.position.y = self.y
        odom.pose.pose.position.z = 0.0
        odom.pose.pose.orientation = quaternion
        odom.twist.twist.linear.x = vx
        odom.twist.twist.linear.y = vy
        odom.twist.twist.angular.z = vth
        self.odom_pub.publish(odom)




def main(args=None):
    rclpy.init(args=args)
    node = DiffTF()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
