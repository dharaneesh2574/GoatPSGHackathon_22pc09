"""
Fleet Manager Module

This module manages a group of robots working together.
Think of it like a command center that:
- Creates and manages robots
- Assigns tasks to robots
- Coordinates robot movements
- Handles robot charging
- Manages traffic between robots

The fleet manager works by:
1. Creating robots when needed
2. Assigning tasks to available robots
3. Making sure robots don't crash into each other
4. Keeping track of robot states and positions
5. Logging all important events
"""

from typing import List, Dict, Optional, Tuple
import random
from src.models.robot import Robot, RobotState
from src.models.nav_graph import NavGraph
from src.controllers.traffic_manager import TrafficManager
from src.utils.logger import FleetLogger

class FleetManager:
    """
    Manages a group of robots working together.
    Think of it like a command center that:
    - Creates and manages robots
    - Assigns tasks to robots
    - Coordinates robot movements
    - Handles robot charging
    - Manages traffic between robots
    """
    
    def __init__(self, nav_graph: NavGraph, logger: FleetLogger):
        """
        Create a new fleet manager.
        - nav_graph: The map robots will move on
        - logger: System for recording fleet events
        """
        self.nav_graph = nav_graph
        self.traffic_manager = TrafficManager(nav_graph, logger)
        self.logger = logger
        self.robots: Dict[int, Robot] = {}
        self.next_robot_id = 0
        self.selected_robot: Optional[Robot] = None
        
        # Generate distinct colors for robots
        self.robot_colors = self._generate_robot_colors()
        
    def _generate_robot_colors(self) -> List[Tuple[int, int, int]]:
        """Generate a list of distinct colors for robots."""
        colors = []
        for i in range(20):  # Support up to 20 robots
            hue = (i * 137.5) % 360  # Golden ratio to spread colors
            # Convert HSV to RGB (simplified)
            h = hue / 360
            s = 0.8
            v = 0.8
            
            # HSV to RGB conversion
            c = v * s
            x = c * (1 - abs((h * 6) % 2 - 1))
            m = v - c
            
            if h < 1/6:
                r, g, b = c, x, 0
            elif h < 2/6:
                r, g, b = x, c, 0
            elif h < 3/6:
                r, g, b = 0, c, x
            elif h < 4/6:
                r, g, b = 0, x, c
            elif h < 5/6:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x
                
            colors.append((int((r + m) * 255), int((g + m) * 255), int((b + m) * 255)))
        return colors
        
    def create_robot(self, start_vertex: int) -> Robot:
        """
        Create a new robot at a specific point.
        - start_vertex: The point where the robot should start
        
        Returns the newly created robot.
        The robot will:
        1. Get a unique ID
        2. Start at the specified point
        3. Be ready to receive tasks
        4. Be logged in the system
        """
        if start_vertex not in range(len(self.nav_graph.vertices)):
            error_msg = f"Invalid vertex index: {start_vertex}"
            self.logger.log_error(error_msg)
            raise ValueError(error_msg)
            
        color = self.robot_colors[self.next_robot_id % len(self.robot_colors)]
        robot = Robot(self.next_robot_id, start_vertex, color)
        self.robots[self.next_robot_id] = robot
        self.next_robot_id += 1
        
        # Request initial vertex occupancy
        self.traffic_manager.request_vertex(robot, start_vertex)
        
        # Log robot creation
        vertex_name = self.nav_graph.get_vertex_name(start_vertex)
        self.logger.log_robot_created(robot.robot_id, start_vertex, vertex_name)
        
        return robot
        
    def select_robot(self, robot_id: int) -> bool:
        """
        Select a robot to give it a task.
        - robot_id: The ID of the robot to select
        
        This method:
        1. Finds the robot by ID
        2. Makes it the selected robot
        3. Logs the selection
        """
        if robot_id in self.robots:
            self.selected_robot = self.robots[robot_id]
            self.logger.log_robot_selection(robot_id)
            return True
        return False
        
    def deselect_robot(self):
        """
        Stop having a robot selected.
        This method:
        1. Clears the selected robot
        2. Logs the deselection
        """
        if self.selected_robot:
            self.logger.log_robot_deselection(self.selected_robot.robot_id)
            self.selected_robot = None
        
    def assign_task(self, target_vertex: int) -> bool:
        """
        Give a task to the selected robot.
        - target_vertex: The point the robot should move to
        
        Returns True if the task was assigned successfully.
        The robot will:
        1. Find the shortest path to the target
        2. Start moving along that path
        3. Update its state to MOVING
        4. Log the task assignment
        """
        if not self.selected_robot or self.selected_robot.state != RobotState.IDLE:
            return False
            
        if target_vertex not in range(len(self.nav_graph.vertices)):
            error_msg = f"Invalid target vertex index: {target_vertex}"
            self.logger.log_error(error_msg)
            return False
            
        # Find path to target
        path = self.nav_graph.find_path(self.selected_robot.current_vertex, target_vertex)
        if not path:
            error_msg = f"No path found from {self.selected_robot.current_vertex} to {target_vertex}"
            self.logger.log_error(error_msg)
            return False
            
        # Assign task to robot
        self.selected_robot.assign_task(target_vertex, path)
        
        # Log task assignment
        self.logger.log_task_assigned(
            self.selected_robot.robot_id,
            self.selected_robot.current_vertex,
            target_vertex,
            path
        )
        
        return True
        
    def update(self, dt: float):
        """
        Update all robots' states over time.
        - dt: Time passed since last update
        
        This method:
        1. Updates each robot's position and state
        2. Handles robot charging
        3. Manages traffic between robots
        4. Logs important state changes
        """
        for robot in self.robots.values():
            old_state = robot.state
            
            # Update robot position
            if robot.state == RobotState.MOVING:
                current_lane = robot.get_current_lane()
                if current_lane:
                    # Release previous lane if moving to a new one
                    if robot.current_lane and robot.current_lane != current_lane:
                        self.traffic_manager.release_lane(robot, robot.current_lane)
                    robot.current_lane = current_lane
                    
                # Update position and check if reached destination
                if robot.update_position(dt):
                    # Release current lane and vertex
                    if robot.current_lane:
                        self.traffic_manager.release_lane(robot, robot.current_lane)
                        robot.current_lane = None
                    self.traffic_manager.release_vertex(robot, robot.current_vertex)
                    robot.current_vertex = robot.target_vertex
                    self.traffic_manager.request_vertex(robot, robot.current_vertex)
                    
                    # Log task completion
                    self.logger.log_task_completed(robot.robot_id, robot.target_vertex)
                    
            # Update traffic management
            self.traffic_manager.update_robot_state(robot, self.nav_graph)
            
            # Log state changes
            if robot.state != old_state:
                self.logger.log_robot_state_change(robot.robot_id, old_state.value, robot.state.value)
            
    def get_robot_at_position(self, pos: Tuple[float, float], radius: float = 0.5) -> Optional[Robot]:
        """
        Find a robot at a specific position.
        - pos: The x, y coordinates to check
        
        Returns the robot at that position, or None if no robot is there.
        """
        for robot in self.robots.values():
            robot_pos = robot.get_position(self.nav_graph)
            dx = robot_pos[0] - pos[0]
            dy = robot_pos[1] - pos[1]
            if (dx * dx + dy * dy) <= radius * radius:
                return robot
        return None
        
    def get_vertex_at_position(self, pos: Tuple[float, float], radius: float = 0.5) -> Optional[int]:
        """
        Find a point near a specific position.
        - pos: The x, y coordinates to check
        
        Returns the index of the nearest point, or None if no point is nearby.
        """
        for vertex_id, vertex_pos in self.nav_graph.vertex_positions.items():
            dx = vertex_pos[0] - pos[0]
            dy = vertex_pos[1] - pos[1]
            if (dx * dx + dy * dy) <= radius * radius:
                return vertex_id
        return None 