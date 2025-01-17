import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist, PoseStamped
from nav2_msgs.action import NavigateToPose
from nav_msgs.msg import Odometry, Path
from sensor_msgs.msg import LaserScan
from rclpy.action import ActionClient
from rclpy.callback_groups import ReentrantCallbackGroup
import csv
from datetime import datetime
import numpy as np
import psutil, os  # Bellek kullanımı için

class Explorer(Node):
    def __init__(self, algorithm):
        super().__init__('explorer_node')
        self.algorithm = algorithm
        self.get_logger().info(f'Using {self.algorithm} for path planning.')
        
        # Publisher: Hedef Nav2'ye iletilecek
        self.pub_goal = self.create_publisher(PoseStamped, '/goal_pose', 10)

        self.sub_path = self.create_subscription(PoseStamped, Path, '/odom', self.path_callback, 10)  # Planned path

        # Subscriber: RViz üzerinden hedef alınacak
        self.sub_goal = self.create_subscription(PoseStamped, '/rviz_goal', self.rviz_goal_callback, 10)

        # NavigateToPose için Action Client
        self.nav_to_pose_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.callback_group = ReentrantCallbackGroup()

        # Robotun pozisyon bilgisi
        self.position = np.array([0.0, 0.0])
        self.start_time = None



    def rviz_goal_callback(self, msg):
        self.get_logger().info(f'Received goal from RViz: x={msg.pose.position.x}, y={msg.pose.position.y}')
        self.start_time = datetime.now()
        self.goal_position = np.array([msg.pose.position.x, msg.pose.position.y])
        self.publish_goal_to_nav2(msg)

    def publish_goal_to_nav2(self, goal_msg):
        goal = NavigateToPose.Goal()
        goal.pose = goal_msg

        self.nav_to_pose_client.wait_for_server()
        self.get_logger().info(f'Publishing goal to Nav2 with {self.algorithm.upper()} algorithm...')
        send_goal_future = self.nav_to_pose_client.send_goal_async(
            goal, feedback_callback=self.feedback_callback, callback_group=self.callback_group
        )
        send_goal_future.add_done_callback(self.goal_response_callback)

    def feedback_callback(self, feedback_msg):
        self.get_logger().info(f'Moving towards goal. Current pose: {feedback_msg.feedback.current_pose}')

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error("Goal command was rejected!")
            return

        self.get_logger().info("Goal command accepted.")
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)

    def result_callback(self, future):
        result = future.result()
        if result.status == NavigateToPose.Result.SUCCESS:
            self.get_logger().info("Successfully reached the goal!")
            self.log_metrics()
        else:
            self.get_logger().error("Failed to reach the goal. Replanning may be required.")

    def log_metrics(self):
        end_time = datetime.now()
        computation_time = (end_time - self.start_time).total_seconds()
        memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024  # MB

        path_length = self.calculate_path_length()
        euclidean_distance = np.linalg.norm(self.goal_position - self.position)

        with open(self.csv_file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([self.algorithm, self.goal_position[0], self.goal_position[1], path_length, 
                             euclidean_distance, computation_time, memory_usage])
        self.get_logger().info("Metrics logged successfully.")

    def calculate_path_length(self, path_msg):
        """calculate total path length."""
        length = 0.0
        for i in range(1, len(path_msg.poses)):
            p1 = path_msg.poses[i - 1].pose.position
            p2 = path_msg.poses[i].pose.position
            length += ((p1.x - p2.x)**2 + (p1.y - p2.y)**2)**0.5
        return length


def main(self, args=None):
    rclpy.init(args=args)
    explorer = Explorer()
    try:
        rclpy.spin(explorer)

        # CSV dosyası oluşturma
        self.csv_file = os.path.join(os.getcwd(), f"metrics_{self.algorithm}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        with open(self.csv_file, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Algorithm', 'Goal_X', 'Goal_Y', 'Path_Length', 'Euclidean_Distance', 
                             'Computation_Time', 'Memory_Usage_MB'])

    except KeyboardInterrupt:
        explorer.get_logger().info("Explorer node shutting down.")

    finally:
        explorer.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
