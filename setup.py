from setuptools import find_packages, setup

package_name = 'explore'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', ['launch/nav_simple_astar.launch.py']),
        ('share/' + package_name + '/launch', ['launch/nav_simple_dijkstra.launch.py']),
        ('share/' + package_name + '/launch', ['launch/nav_complex_astar.launch.py']),
        ('share/' + package_name + '/launch', ['launch/nav_complex_dijkstra.launch.py']),
        ('share/' + package_name + '/launch', ['launch/nav_moderate_astar.launch.py']),
        ('share/' + package_name + '/launch', ['launch/nav_moderate_dijkstra.launch.py']),
        
        ('share/' + package_name + '/launch', ['launch/robot_state_publisher.launch.py']),
        ('share/' + package_name + '/launch', ['launch/spawn_turtlebot3.launch.py']),
        ('share/' + package_name + '/rviz', ['rviz/tb3_gazebo.rviz']),

        # Harita dosyaları
        ('share/' + package_name + '/maps', ['maps/nav_moderate.yaml', 'maps/nav_moderate.pgm']),
        ('share/' + package_name + '/maps', ['maps/nav_simple.yaml', 'maps/nav_simple.pgm']),
        ('share/' + package_name + '/maps', ['maps/nav_complex.yaml', 'maps/nav_complex.pgm']),

        ('share/' + package_name + '/worlds', ['worlds/nav_complex.world']),
        ('share/' + package_name + '/worlds', ['worlds/nav_simple.world']),
        ('share/' + package_name + '/worlds', ['worlds/nav_moderate.world']),
        
        ('share/' + package_name + '/config', ['config/nav2_params_astar.yaml']),
        ('share/' + package_name + '/config', ['config/nav2_params_dijkstra.yaml']),
        ('share/' + package_name + '/config', ['config/nav2_params.yaml']),

    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='kaplan',
    maintainer_email='007kaplankaplan@gmail.com',
    description='TODO: Package description',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['explore = explore.test:main',
        ],
    },
)
