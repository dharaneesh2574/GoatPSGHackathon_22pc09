import logging
import os
from datetime import datetime
from typing import Optional

class FleetLogger:
    def __init__(self, log_file: str = "fleet_logs.txt"):
        # Create logs directory if it doesn't exist
        os.makedirs("logs", exist_ok=True)
        
        # Set up logging
        self.logger = logging.getLogger("FleetManagement")
        self.logger.setLevel(logging.INFO)
        
        # Create file handler
        log_path = os.path.join("logs", log_file)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.INFO)
        
        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
    def log_robot_created(self, robot_id: int, vertex_id: int, vertex_name: str):
        """Log when a new robot is created."""
        self.logger.info(f"Robot {robot_id} created at vertex {vertex_id} ({vertex_name})")
        
    def log_task_assigned(self, robot_id: int, start_vertex: int, target_vertex: int, path: list):
        """Log when a task is assigned to a robot."""
        self.logger.info(f"Task assigned to Robot {robot_id}: {start_vertex} -> {target_vertex}")
        self.logger.info(f"Path: {' -> '.join(map(str, path))}")
        
    def log_robot_state_change(self, robot_id: int, old_state: str, new_state: str):
        """Log when a robot's state changes."""
        self.logger.info(f"Robot {robot_id} state changed: {old_state} -> {new_state}")
        
    def log_lane_occupancy(self, lane: tuple, robot_id: int, is_occupied: bool):
        """Log when a lane's occupancy changes."""
        action = "occupied" if is_occupied else "released"
        self.logger.info(f"Lane {lane} {action} by Robot {robot_id}")
        
    def log_vertex_occupancy(self, vertex_id: int, robot_id: int, is_occupied: bool):
        """Log when a vertex's occupancy changes."""
        action = "occupied" if is_occupied else "released"
        self.logger.info(f"Vertex {vertex_id} {action} by Robot {robot_id}")
        
    def log_task_completed(self, robot_id: int, target_vertex: int):
        """Log when a robot completes its task."""
        self.logger.info(f"Robot {robot_id} completed task at vertex {target_vertex}")
        
    def log_error(self, message: str):
        """Log an error message."""
        self.logger.error(message) 