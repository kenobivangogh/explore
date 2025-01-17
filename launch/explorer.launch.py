from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
import os

def set_algorithm_param(context, *args, **kwargs):
    # Algoritma parametresini alıyoruz
    package_dir = get_package_share_directory('explore')
    world_file = os.path.join(package_dir, 'worlds', 'nav_complex.world')
    algorithm = LaunchConfiguration('algorithm').perform(context)
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    map_file = os.path.join(package_dir, 'maps', 'nav_complex.yaml')
    # Algoritmaya göre nav2_params dosyasını seçiyoruz
    if algorithm == 'astar':
        config_path = os.path.join(
            get_package_share_directory('explore'), 'config', 'nav2_params_astar.yaml'
        )
    else:  # 'dijkstra' seçildiğinde
        config_path = os.path.join(
            get_package_share_directory('explore'), 'config', 'nav2_params_dijkstra.yaml'
        )
    
    # Planner ve explorer düğümleri
    return LaunchDescription[
                # Gazebo
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')
            ),
            launch_arguments={'world': world_file}.items()
        ),
                # Nav2 Bringup
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('nav2_bringup'), 'launch', 'bringup_launch.py')
            ),
            launch_arguments={
                'map': map_file,
                'use_sim_time': use_sim_time,
                'params_file': [config_path],
            }.items()
        ),
        # NavFn planner düğümü - Global planner
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            output='screen',
            parameters=[config_path]
        ),
        
        # Explorer Node
        Node(
            package='explore',
            executable='explore',
            name='explorer_node',
            parameters=[{'algorithm': algorithm}],
            output='screen'
        ),
    ]

def generate_launch_description():
    # Dinamik parametreler
    algorithm = LaunchConfiguration('algorithm', default='astar')
    world = LaunchConfiguration('world', default='nav_simple')
    

    # Dosya yolları
    

    
    
    rviz_config_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'rviz', 'nav2_default_view.rviz')

    # Launch Description
    return LaunchDescription([
        # Argümanlar


        # TurtleBot3
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'launch', 'robot_state_publisher.launch.py')
            )
        ),
        
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('turtlebot3_gazebo'), 'launch', 'spawn_turtlebot3.launch.py')
            )
        ),    



        # RViz
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_dir],
            parameters=[{'use_sim_time': False}],
            output='screen'
        ),


    ])
