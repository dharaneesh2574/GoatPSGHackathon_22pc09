"""
Robot Module

This module implements a robot that can:
- Move between points in the navigation graph
- Carry out tasks
- Manage its battery level
- Handle charging when needed
- Avoid collisions with other robots

Think of it like a delivery robot that:
- Can only move along predefined paths
- Needs to recharge its battery
- Can pick up and deliver items
- Has to wait if another robot is in its way
"""

from enum import Enum
from typing import List, Tuple, Optional
from .nav_graph import NavGraph

class RobotState(Enum):
    """
    Different states a robot can be in:
    - IDLE: Robot is waiting for a task
    - MOVING: Robot is traveling to its destination
    - WAITING: Robot is waiting for a path to clear
    - CHARGING: Robot is recharging its battery
    - TASK_COMPLETE: Robot has finished its task
    """
    IDLE = "IDLE"
    MOVING = "MOVING"
    WAITING = "WAITING"
    CHARGING = "CHARGING"
    TASK_COMPLETE = "TASK_COMPLETE"

class Robot:
    """
    A robot that can move through the navigation graph and perform tasks.
    Think of it like a delivery robot that:
    - Has a unique ID
    - Can move between points
    - Has a battery that needs recharging
    - Can be assigned tasks
    - Has to avoid other robots
    """
    
    def __init__(self, robot_id: int, start_vertex: int, nav_graph: NavGraph):
        """
        Create a new robot at a specific point in the navigation graph.
        - robot_id: Unique identifier for this robot
        - start_vertex: The point where the robot starts
        - nav_graph: The map the robot will move on
        """
        self.robot_id = robot_id
        self.current_vertex = start_vertex
        self.current_lane = None
        self.target_vertex = None
        self.path = []
        self.nav_graph = nav_graph
        self.state = RobotState.IDLE
        self.battery_level = 100.0
        self.charging_rate = 5.0
        self.discharging_rate = 1.0
        
    def get_position(self, nav_graph: NavGraph) -> Tuple[float, float]:
        """
        Get the current position of the robot.
        If the robot is moving between points, calculate its exact position.
        Returns the x, y coordinates of the robot
        """
        if self.current_lane:
            # If robot is moving, calculate its position along the lane
            start_pos, end_pos = nav_graph.get_lane_vertices(self.current_lane)
            # Calculate how far along the lane the robot has moved
            progress = self.path_progress / 100.0
            return (
                start_pos[0] + (end_pos[0] - start_pos[0]) * progress,
                start_pos[1] + (end_pos[1] - start_pos[1]) * progress
            )
        else:
            # If robot is at a point, return that point's position
            return nav_graph.get_vertex_position(self.current_vertex)
            
    def get_current_lane(self) -> Optional[Tuple[int, int]]:
        """
        Get the lane the robot is currently moving on.
        Returns None if the robot is not moving
        """
        return self.current_lane
        
    def update(self, delta_time: float) -> None:
        """
        Update the robot's state over time.
        - delta_time: Time passed since last update
        
        This method:
        1. Updates battery level
        2. Handles charging if at a charging station
        3. Moves the robot along its path if moving
        4. Updates robot's state based on its progress
        """
        # Update battery level
        if self.state == RobotState.CHARGING:
            self.battery_level = min(100.0, self.battery_level + self.charging_rate * delta_time)
        else:
            self.battery_level = max(0.0, self.battery_level - self.discharging_rate * delta_time)
            
        # Handle charging at charging stations
        if self.state == RobotState.IDLE and self.nav_graph.is_charger(self.current_vertex):
            self.state = RobotState.CHARGING
            return
            
        # Move along path if moving
        if self.state == RobotState.MOVING and self.path:
            self.path_progress += delta_time * 10.0  # Speed of movement
            if self.path_progress >= 100.0:
                self.path_progress = 0.0
                self.current_vertex = self.path.pop(0)
                if self.path:
                    self.current_lane = (self.current_vertex, self.path[0])
                else:
                    self.current_lane = None
                    self.state = RobotState.IDLE
                    if self.target_vertex == self.current_vertex:
                        self.state = RobotState.TASK_COMPLETE
                        
    def assign_task(self, target_vertex: int) -> bool:
        """
        Assign a new task to the robot.
        - target_vertex: The point the robot should move to
        
        Returns True if the task was assigned successfully.
        The robot will:
        1. Find the shortest path to the target
        2. Start moving along that path
        3. Update its state to MOVING
        """
        if self.state != RobotState.IDLE:
            return False
            
        self.target_vertex = target_vertex
        self.path = self.nav_graph.find_shortest_path(self.current_vertex, target_vertex)
        if self.path:
            self.path.pop(0)  # Remove current vertex from path
            if self.path:
                self.current_lane = (self.current_vertex, self.path[0])
                self.state = RobotState.MOVING
                self.path_progress = 0.0
            return True
        return False 