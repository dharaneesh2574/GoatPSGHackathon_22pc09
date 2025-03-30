from enum import Enum
from typing import List, Tuple, Optional
import numpy as np

class RobotState(Enum):
    IDLE = "idle"
    MOVING = "moving"
    WAITING = "waiting"
    CHARGING = "charging"
    TASK_COMPLETE = "task_complete"

class Robot:
    def __init__(self, robot_id: int, start_vertex: int, color: Tuple[int, int, int]):
        self.robot_id = robot_id
        self.current_vertex = start_vertex
        self.target_vertex = None
        self.path = []
        self.current_path_index = 0
        self.state = RobotState.IDLE
        self.color = color
        self.current_lane = None
        self.progress = 0.0  # Progress along current lane (0.0 to 1.0)
        self.speed = 0.3  # Movement speed
        
    def assign_task(self, target_vertex: int, path: List[int]):
        """Assign a new navigation task to the robot."""
        self.target_vertex = target_vertex
        self.path = path
        self.current_path_index = 0
        self.state = RobotState.MOVING
        self.progress = 0.0
        
    def update_position(self, dt: float) -> bool:
        """Update robot position along its path. Returns True if reached destination."""
        if self.state != RobotState.MOVING or not self.path:
            return False
            
        if self.current_path_index >= len(self.path) - 1:
            self.state = RobotState.TASK_COMPLETE
            return True
            
        # Update progress along current lane
        self.progress += self.speed * dt
        
        if self.progress >= 1.0:
            self.progress = 0.0
            self.current_path_index += 1
            if self.current_path_index >= len(self.path) - 1:
                self.state = RobotState.TASK_COMPLETE
                return True
                
        return False
        
    def get_current_lane(self) -> Optional[Tuple[int, int]]:
        """Get the current lane the robot is moving on."""
        if not self.path or self.current_path_index >= len(self.path) - 1:
            return None
        return (self.path[self.current_path_index], self.path[self.current_path_index + 1])
        
    def get_position(self, nav_graph) -> Tuple[float, float]:
        """Get the current position of the robot."""
        if not self.path or self.current_path_index >= len(self.path) - 1:
            return nav_graph.get_vertex_position(self.current_vertex)
            
        start_vertex = self.path[self.current_path_index]
        end_vertex = self.path[self.current_path_index + 1]
        start_pos = nav_graph.get_vertex_position(start_vertex)
        end_pos = nav_graph.get_vertex_position(end_vertex)
        
        # Interpolate between start and end positions based on progress
        x = start_pos[0] + (end_pos[0] - start_pos[0]) * self.progress
        y = start_pos[1] + (end_pos[1] - start_pos[1]) * self.progress
        return (x, y)
        
    def set_waiting(self):
        """Set robot to waiting state."""
        self.state = RobotState.WAITING
        
    def set_moving(self):
        """Set robot back to moving state."""
        self.state = RobotState.MOVING 