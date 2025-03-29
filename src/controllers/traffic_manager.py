from typing import Dict, List, Set, Tuple, Optional
from src.models.robot import Robot, RobotState
from src.utils.logger import FleetLogger

class TrafficManager:
    def __init__(self):
        self.occupied_lanes: Dict[Tuple[int, int], List[Robot]] = {}
        self.vertex_occupancy: Dict[int, Set[Robot]] = {}
        self.logger = FleetLogger()
        
    def request_lane(self, robot: Robot, lane: Tuple[int, int]) -> bool:
        """Request permission to use a lane. Returns True if granted."""
        if lane not in self.occupied_lanes:
            self.occupied_lanes[lane] = []
            
        # If lane is empty or robot is already in the queue, grant access
        if not self.occupied_lanes[lane] or robot in self.occupied_lanes[lane]:
            if robot not in self.occupied_lanes[lane]:
                self.occupied_lanes[lane].append(robot)
                self.logger.log_lane_occupancy(lane, robot.robot_id, True)
            return True
            
        return False
        
    def release_lane(self, robot: Robot, lane: Tuple[int, int]):
        """Release a lane that was previously occupied by a robot."""
        if lane in self.occupied_lanes and robot in self.occupied_lanes[lane]:
            self.occupied_lanes[lane].remove(robot)
            self.logger.log_lane_occupancy(lane, robot.robot_id, False)
            if not self.occupied_lanes[lane]:
                del self.occupied_lanes[lane]
                
    def request_vertex(self, robot: Robot, vertex: int) -> bool:
        """Request permission to occupy a vertex. Returns True if granted."""
        if vertex not in self.vertex_occupancy:
            self.vertex_occupancy[vertex] = set()
            
        # If vertex is empty or robot is already there, grant access
        if not self.vertex_occupancy[vertex] or robot in self.vertex_occupancy[vertex]:
            self.vertex_occupancy[vertex].add(robot)
            return True
            
        return False
        
    def release_vertex(self, robot: Robot, vertex: int):
        """Release a vertex that was previously occupied by a robot."""
        if vertex in self.vertex_occupancy and robot in self.vertex_occupancy[vertex]:
            self.vertex_occupancy[vertex].remove(robot)
            if not self.vertex_occupancy[vertex]:
                del self.vertex_occupancy[vertex]
                
    def update_robot_state(self, robot: Robot, nav_graph):
        """Update robot state based on traffic conditions."""
        if robot.state == RobotState.MOVING:
            current_lane = robot.get_current_lane()
            if current_lane:
                if not self.request_lane(robot, current_lane):
                    robot.set_waiting()
                else:
                    robot.set_moving()
                    
        elif robot.state == RobotState.WAITING:
            current_lane = robot.get_current_lane()
            if current_lane and self.request_lane(robot, current_lane):
                robot.set_moving()
                
    def get_occupied_lanes(self) -> List[Tuple[int, int]]:
        """Get list of currently occupied lanes."""
        return list(self.occupied_lanes.keys())
        
    def get_robots_in_lane(self, lane: Tuple[int, int]) -> List[Robot]:
        """Get list of robots currently in a lane."""
        return self.occupied_lanes.get(lane, [])
        
    def get_robots_at_vertex(self, vertex: int) -> Set[Robot]:
        """Get set of robots currently at a vertex."""
        return self.vertex_occupancy.get(vertex, set()) 