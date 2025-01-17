import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import Odometry, Path
from sensor_msgs.msg import LaserScan
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
from action_msgs.msg import GoalStatus
import csv
from datetime import datetime
import numpy as np
import psutil, os # bellek kullanımı 

class Explorer(Node):
    def __init__(self):
        super().__init__('explorer_node')
        # ROS 2 parametresinden algorithm değerini alır
        self.algorithm = self.declare_parameter('algorithm', 'astar').get_parameter_value().string_value
        self.get_logger().info(f'Using {self.algorithm} for path planning.')
        
        # Publisher: Hedef Nav2'ye iletilecek
        # self.pub_goal = self.create_publisher(PoseStamped, '/goal_pose', 10)

        self.sub_odom = self.create_subscription(Odometry, '/odom', self.path_callback, 10) 

        # Subscriber: RViz üzerinden hedef alınacak
        #self.sub_goal = self.create_subscription(PoseStamped, '/rviz_goal', self.rviz_goal_callback, 10)
        self.sub_goal = self.create_subscription(PoseStamped, '/goal_pose', self.rviz_goal_callback, 10)

        # NavigateToPose için Action Client
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.callback_group = ReentrantCallbackGroup()

        # Robotun pozisyon bilgisi
        self.position = np.array([0.0, 0.0])
        self.start_time = None

        self.last_microsecond=0
        self.last_x=0.0
        self.last_y=0.0

        # comparison metrics
        self.csv_file = f"metrics_{self.algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        with open(self.csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Algorithm', 'Goal_X', 'Goal_Y', 'Path_Length', 'Euclidean_Distance', 'Computation_Time', 'Memory_Usage_MB', 'Waypoint_Count'])

    def path_callback(self, msg: Odometry):
        """Process the planned path and calculate metrics."""
        if msg is None:
            self.get_logger().error("No valid path found!")
            return

        # Calculate metrics
        end_time = datetime.now()
        computation_time = (end_time.microsecond - self.last_microsecond) / 1e6
        now = msg.pose.pose.position
        euclidean_distance = np.sqrt((now.x - self.last_x)**2+(now.y - self.last_y)**2)
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)  # MB

        self.last_x = now.x
        self.last_y = now.y

        # Save metrics to CSV
        with open(self.csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.algorithm, now.x, now.y, 0, euclidean_distance, computation_time, memory_usage, 0])

        # self.get_logger().info(f"Metrics saved to {self.csv_file}")
        # self.get_logger().info(f"Odometry mesajı alındı: Position: x={msg.pose.pose.position.x}, y={msg.pose.pose.position.y}")

    def rviz_goal_callback(self, msg):
        """
        RViz üzerinden gelen hedefi alır ve Nav2'ye gönderir.
        """
        self.get_logger().info(f'Received goal from RViz: x={msg.pose.position.x}, y={msg.pose.position.y}')
        self.publish_goal_to_nav2(msg)

    def publish_goal_to_nav2(self, goal_msg):
        """
        Hedefi NavigateToPose eylemiyle Nav2'ye iletir.
        """
        # NavigateToPose eylemi için hedef mesajı oluştur
        goal = NavigateToPose.Goal()
        goal.pose = goal_msg

        # NavigateToPose server'ına bağlan
        self.nav_to_pose_client.wait_for_server()

        # Görev gönder ve geri bildirim al
        self.get_logger().info(f'Publishing goal to Nav2 with {self.algorithm.upper()} algorithm...')
        send_goal_future = self.nav_to_pose_client.send_goal_async(
            goal, feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        """
        Hedefe giderken geri bildirim alır.
        """
        # self.get_logger().info(f'Moving towards goal. Current pose: {feedback_msg.feedback.current_pose}')

    def goal_response_callback(self, future):
        """
        Hedef komutunun durumunu işler.
        """
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal command was rejected!")
            return

        self.get_logger().info("Goal command accepted.")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result()
        if result.status == GoalStatus.STATUS_SUCCEEDED:
            self.get_logger().info("Goal succeeded!")
        elif result.status == GoalStatus.STATUS_ABORTED:
            self.get_logger().info("Goal aborted!")
        elif result.status == GoalStatus.STATUS_CANCELED:
            self.get_logger().info("Goal canceled!")
        else:
            self.get_logger().info(f"Goal failed with status: {result.status}")


def main(args=None):
    rclpy.init(args=args)
    explorer = Explorer()
    try:
        rclpy.spin(explorer)
    except KeyboardInterrupt:
        explorer.get_logger().info("Explorer node shutting down.")
    finally:
        explorer.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()