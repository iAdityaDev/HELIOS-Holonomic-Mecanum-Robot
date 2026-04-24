import rclpy
from rclpy.node import Node
from std_msgs.msg import Int64


class HighSpeedForwardEncoder(Node):
    def __init__(self):
        super().__init__('high_speed_forward_encoder')
        self.get_logger().info("🚗 High-Speed Forward Encoder Publisher Started")

        # Publishers
        self.pub_fr = self.create_publisher(Int64, '/fr_encoder_ticks', 10)
        self.pub_fl = self.create_publisher(Int64, '/fl_encoder_ticks', 10)
        self.pub_rr = self.create_publisher(Int64, '/rr_encoder_ticks', 10)
        self.pub_rl = self.create_publisher(Int64, '/rl_encoder_ticks', 10)

        # Encoder values
        self.current_ticks = {"fr": 0, "fl": 0, "rr": 0, "rl": 0}

        # High-speed parameters
        self.tick_rate = 50.0          # publish at 50 Hz (faster)
        self.tick_increment = 20       # high-speed tick increment

        # Timer
        self.create_timer(1.0 / self.tick_rate, self.publish_forward_ticks)

    def publish_forward_ticks(self):
        # Increase all wheel encoders equally → forward motion
        for k in self.current_ticks:
            self.current_ticks[k] += self.tick_increment

        # Publish
        self.pub_fr.publish(Int64(data=self.current_ticks["fr"]))
        self.pub_fl.publish(Int64(data=self.current_ticks["fl"]))
        self.pub_rr.publish(Int64(data=self.current_ticks["rr"]))
        self.pub_rl.publish(Int64(data=self.current_ticks["rl"]))

        self.get_logger().info(
            f"FORWARD FAST | FR:{self.current_ticks['fr']} "
            f"FL:{self.current_ticks['fl']} RR:{self.current_ticks['rr']} "
            f"RL:{self.current_ticks['rl']}"
        )


def main(args=None):
    rclpy.init(args=args)
    node = HighSpeedForwardEncoder()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info("🛑 Stopped Encoder Publisher.")
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
