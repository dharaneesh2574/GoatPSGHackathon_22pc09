"""
Navigation Graph Module

This module implements a simple navigation system that works like a road map:
- Vertices are like intersections or points where robots can stop
- Lanes are like roads connecting these points
- Each lane has a length (like distance between points)
- Some points are charging stations where robots can recharge

Think of it like a simplified city map where:
- Robots can only move along predefined paths (lanes)
- They can only stop at specific points (vertices)
- They need to plan their route from one point to another
- They can recharge at special charging stations
"""

import json
from typing import List, Dict, Tuple, Optional, Set
import numpy as np
import math

class NavGraph:
    """
    A navigation graph that represents a network of connected points (vertices) and paths (lanes).
    Think of it like a simplified road map where:
    - Vertices are like intersections where robots can stop
    - Lanes are like roads connecting these intersections
    - Each lane has a length (distance between points)
    - Some points are charging stations where robots can recharge
    """
    
    def __init__(self, graph_file: str):
        """
        Initialize a navigation graph from a JSON file.
        - graph_file: Path to the JSON file containing the graph data
        """
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
        """
        Get the position (x, y) of a specific point.
        - vertex_id: Index of the point to look up
        Returns the x, y coordinates of the point
        """
        return self.vertex_positions[vertex_id]
    
    def get_vertex_name(self, vertex_id: int) -> str:
        """Get the name of a vertex."""
        return self.vertex_names[vertex_id]
    
    def is_charger(self, vertex_id: int) -> bool:
        """Check if a vertex is a charging station."""
        return self.chargers[vertex_id]
    
    def get_neighbors(self, vertex_id: int) -> List[int]:
        """
        Find all points that are directly connected to a given point.
        - vertex_id: Index of the point to check
        Returns a list of indices of connected points
        """
        return self.adjacency_list[vertex_id]
    
    def get_lane_vertices(self, lane: Tuple[int, int]) -> Tuple[Tuple[float, float], Tuple[float, float]]:
        """Get the coordinates of both vertices of a lane."""
        return (self.get_vertex_position(lane[0]), self.get_vertex_position(lane[1]))
    
    def get_lane_length(self, start: int, end: int) -> float:
        """
        Calculate the distance between two connected points.
        - start: Index of the starting point
        - end: Index of the ending point
        Returns the distance between the points
        """
        start_pos = self.get_vertex_position(start)
        end_pos = self.get_vertex_position(end)
        return math.sqrt((end_pos[0] - start_pos[0])**2 + (end_pos[1] - start_pos[1])**2)
    
    def find_shortest_path(self, start: int, end: int) -> List[int]:
        """
        Find the shortest route between two points using Dijkstra's algorithm.
        Think of it like finding the quickest way to drive from one place to another:
        1. Start at the beginning point
        2. Look at all connected points and find the closest one
        3. Move to that point and repeat until reaching the destination
        4. Keep track of the path taken to get there
        
        - start: Index of the starting point
        - end: Index of the ending point
        Returns a list of point indices representing the shortest path
        """
        # Initialize distances to all points as infinity (very far)
        distances = {v: float('inf') for v in range(len(self.vertices))}
        distances[start] = 0  # Distance to start point is 0
        previous = {v: None for v in range(len(self.vertices))}  # Keep track of path
        unvisited = set(range(len(self.vertices)))  # Points we haven't checked yet
        
        while unvisited:
            # Find the unvisited point with the shortest distance
            current = min(unvisited, key=lambda v: distances[v])
            if current == end:  # We reached our destination
                break
                
            unvisited.remove(current)  # Mark this point as visited
            
            # Check all connected points
            for neighbor in self.get_neighbors(current):
                if neighbor in unvisited:
                    # Calculate distance to this neighbor
                    distance = distances[current] + self.get_lane_length(current, neighbor)
                    # If this is a shorter path, update it
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        previous[neighbor] = current
        
        # Build the path by following the previous points from end to start
        path = []
        current = end
        while current is not None:
            path.append(current)
            current = previous[current]
        return list(reversed(path))  # Reverse to get path from start to end 