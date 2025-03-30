import json
from typing import List, Dict, Tuple, Optional
import numpy as np

class NavGraph:
    def __init__(self, graph_file: str):
        with open(graph_file, 'r') as f:
            self.graph_data = json.load(f)
        
        self.vertices = self.graph_data['levels']['level1']['vertices']
        self.lanes = self.graph_data['levels']['level1']['lanes']
        self.vertex_positions = {i: (v[0], v[1]) for i, v in enumerate(self.vertices)}
        self.vertex_names = {i: v[2].get('name', '') for i, v in enumerate(self.vertices)}
        self.chargers = {i: v[2].get('is_charger', False) for i, v in enumerate(self.vertices)}
        
        # Create adjacency list for easier path finding
        self.adjacency_list = {}
        for i in range(len(self.vertices)):
            self.adjacency_list[i] = []
            for lane in self.lanes:
                if lane[0] == i:
                    self.adjacency_list[i].append(lane[1])
                elif lane[1] == i:
                    self.adjacency_list[i].append(lane[0])
    
    def get_vertex_position(self, vertex_id: int) -> Tuple[float, float]:
        """Get the (x, y) coordinates of a vertex."""
        return self.vertex_positions[vertex_id]
    
    def get_vertex_name(self, vertex_id: int) -> str:
        """Get the name of a vertex."""
        return self.vertex_names[vertex_id]
    
    def is_charger(self, vertex_id: int) -> bool:
        """Check if a vertex is a charging station."""
        return self.chargers[vertex_id]
    
    def get_neighbors(self, vertex_id: int) -> List[int]:
        """Get all neighboring vertices of a given vertex."""
        return self.adjacency_list[vertex_id]
    
    def find_path(self, start: int, end: int) -> List[int]:
        """Find a path between two vertices using BFS."""
        queue = [(start, [start])]
        visited = {start}
        
        while queue:
            (vertex, path) = queue.pop(0)
            for next_vertex in self.get_neighbors(vertex):
                if next_vertex == end:
                    return path + [next_vertex]
                if next_vertex not in visited:
                    visited.add(next_vertex)
                    queue.append((next_vertex, path + [next_vertex]))
        
        return []  # No path found
    
    def get_lane_vertices(self, lane: Tuple[int, int]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Get the coordinates of both vertices of a lane."""
        return (self.get_vertex_position(lane[0]), self.get_vertex_position(lane[1])) 