"""
Fleet GUI Module

This module creates a visual interface for the fleet management system.
Think of it like a control panel that:
- Shows the map where robots move
- Displays all robots and their states
- Lets you create and control robots
- Shows important information about the system
- Provides visual feedback for all actions

The GUI works by:
1. Drawing the map and all its elements
2. Showing robots and their movements
3. Handling mouse clicks to control robots
4. Displaying messages about what's happening
5. Showing a legend with system information
"""

import pygame
import sys
from typing import Tuple, Optional
from src.controllers.fleet_manager import FleetManager
from src.models.nav_graph import NavGraph
from src.models.robot import RobotState

class FleetGUI:
    """
    Creates a visual interface for the fleet management system.
    Think of it like a control panel that:
    - Shows the map where robots move
    - Displays all robots and their states
    - Lets you create and control robots
    - Shows important information about the system
    - Provides visual feedback for all actions
    """
    
    def __init__(self, fleet_manager: FleetManager, width: int = 1200, height: int = 800):
        """
        Create a new GUI window.
        - fleet_manager: The system that manages the robots
        - width: Width of the window in pixels
        - height: Height of the window in pixels
        """
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Fleet Management System")
        
        self.fleet_manager = fleet_manager
        self.width = width
        self.height = height
        
        # Colors for different elements
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.CYAN = (0, 255, 255)
        
        # Different text sizes for different purposes
        self.font = pygame.font.Font(None, 36)  # Large font for vertex names
        self.message_font = pygame.font.Font(None, 24)  # Medium font for action messages
        self.legend_font = pygame.font.Font(None, 20)  # Small font for legend
        
        # Calculate how to show the map in the window
        self._calculate_view_transform()
        
        # System for showing temporary messages
        self.action_messages = []
        self.message_duration = 3.0  # How long messages stay on screen
        self.message_start_time = 0
        
        # Size and position of the information panel
        self.legend_width = 250
        self.legend_height = 200
        self.legend_x = width - self.legend_width - 20
        self.legend_y = 20
        
        # Help screen settings
        self.show_help = False
        self.help_text = [
            "Left Click Vertex: Create Robot",
            "Left Click Robot: Select Robot",
            "Left Click Vertex + Selected Robot: Assign Task",
            "Right Click: Deselect Robot, H: Toggle Help"
        ]
        
    def _calculate_view_transform(self):
        """
        Figure out how to show the map in the window.
        This method:
        1. Finds the size of the map
        2. Calculates how to scale it to fit the window
        3. Figures out where to position it in the window
        """
        # Find the map's boundaries
        min_x = min(v[0] for v in self.fleet_manager.nav_graph.vertices)
        max_x = max(v[0] for v in self.fleet_manager.nav_graph.vertices)
        min_y = min(v[1] for v in self.fleet_manager.nav_graph.vertices)
        max_y = max(v[1] for v in self.fleet_manager.nav_graph.vertices)
        
        # Calculate how to scale the map
        map_width = max_x - min_x
        map_height = max_y - min_y
        scale_x = (self.width - 100) / map_width
        scale_y = (self.height - 100) / map_height
        self.scale = min(scale_x, scale_y)
        
        # Calculate where to position the map
        self.offset_x = (self.width - map_width * self.scale) / 2
        self.offset_y = (self.height - map_height * self.scale) / 2
        
    def world_to_screen(self, pos: Tuple[float, float]) -> Tuple[int, int]:
        """
        Convert map coordinates to screen coordinates.
        - pos: A position on the map (x, y)
        Returns the position on the screen (x, y)
        """
        return (
            int(pos[0] * self.scale + self.offset_x),
            int(pos[1] * self.scale + self.offset_y)
        )
        
    def screen_to_world(self, pos: Tuple[int, int]) -> Tuple[float, float]:
        """
        Convert screen coordinates to map coordinates.
        - pos: A position on the screen (x, y)
        Returns the position on the map (x, y)
        """
        return (
            (pos[0] - self.offset_x) / self.scale,
            (pos[1] - self.offset_y) / self.scale
        )
        
    def add_action_message(self, message: str, color: Tuple[int, int, int]):
        """
        Add a temporary message to the screen.
        - message: The text to show
        - color: The color of the text
        """
        self.action_messages.append({
            'text': message,
            'color': color,
            'start_time': pygame.time.get_ticks()
        })
        
    def draw_vertex(self, pos: Tuple[float, float], name: str, is_charger: bool):
        """
        Draw a point on the map.
        - pos: The position of the point
        - name: The label for the point
        - is_charger: Whether this is a charging station
        """
        screen_pos = self.world_to_screen(pos)
        
        # Draw the point
        pygame.draw.circle(self.screen, self.WHITE, screen_pos, 8)
        
        # Draw charging station indicator if needed
        if is_charger:
            pygame.draw.circle(self.screen, self.CYAN, screen_pos, 12, 2)
            
        # Draw the point's name
        text = self.font.render(name, True, self.WHITE)
        text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - 20))
        self.screen.blit(text, text_rect)
        
    def draw_lane(self, start_pos: Tuple[float, float], end_pos: Tuple[float, float], is_occupied: bool):
        """
        Draw a path between two points.
        - start_pos: Starting point of the path
        - end_pos: Ending point of the path
        - is_occupied: Whether a robot is using this path
        """
        screen_start = self.world_to_screen(start_pos)
        screen_end = self.world_to_screen(end_pos)
        
        # Draw the path
        if is_occupied:
            # If path is in use, draw it red with a white line on top
            pygame.draw.line(self.screen, self.RED, screen_start, screen_end, 6)
            pygame.draw.line(self.screen, self.WHITE, screen_start, screen_end, 2)
        else:
            # If path is free, draw it gray
            pygame.draw.line(self.screen, self.GRAY, screen_start, screen_end, 4)
            
    def draw_robot(self, robot, pos: Tuple[float, float]):
        """
        Draw a robot on the map.
        - robot: The robot to draw
        - pos: The robot's position
        """
        screen_pos = self.world_to_screen(pos)
        
        # Draw the robot
        pygame.draw.circle(self.screen, self.WHITE, screen_pos, 12)
        
        # Draw status indicator based on robot's state
        if robot.state == RobotState.MOVING:
            pygame.draw.circle(self.screen, self.GREEN, screen_pos, 15, 3)
        elif robot.state == RobotState.WAITING:
            pygame.draw.circle(self.screen, self.RED, screen_pos, 15, 3)
        elif robot.state == RobotState.CHARGING:
            pygame.draw.circle(self.screen, self.CYAN, screen_pos, 15, 3)
        elif robot.state == RobotState.TASK_COMPLETE:
            pygame.draw.circle(self.screen, self.YELLOW, screen_pos, 15, 3)
            
        # Draw robot ID
        text = self.message_font.render(str(robot.robot_id), True, self.BLACK)
        text_rect = text.get_rect(center=screen_pos)
        self.screen.blit(text, text_rect)
        
    def draw_action_messages(self):
        """
        Draw all temporary messages on the screen.
        Messages appear in the top-right corner and disappear after 3 seconds.
        """
        current_time = pygame.time.get_ticks()
        y_offset = 50
        
        # Draw each message
        for msg in self.action_messages[:]:
            elapsed = (current_time - msg['start_time']) / 1000.0
            if elapsed < self.message_duration:
                text = self.message_font.render(msg['text'], True, msg['color'])
                self.screen.blit(text, (self.width - text.get_width() - 20, y_offset))
                y_offset += 30
            else:
                self.action_messages.remove(msg)
                
    def draw_legend(self):
        """
        Draw the information panel in the top-right corner.
        Shows:
        - Total number of robots
        - Number of waiting robots
        - Number of occupied paths
        - What different robot colors mean
        """
        # Draw panel background
        pygame.draw.rect(self.screen, (0, 0, 0, 128), 
                        (self.legend_x, self.legend_y, self.legend_width, self.legend_height))
        pygame.draw.rect(self.screen, self.WHITE,
                        (self.legend_x, self.legend_y, self.legend_width, self.legend_height), 2)
        
        # Draw title
        title = self.legend_font.render("Fleet Status", True, self.WHITE)
        self.screen.blit(title, (self.legend_x + 10, self.legend_y + 10))
        
        # Draw robot counts
        y_offset = self.legend_y + 40
        total_robots = len(self.fleet_manager.robots)
        waiting_robots = sum(1 for r in self.fleet_manager.robots.values() 
                           if r.state == RobotState.WAITING)
        occupied_lanes = len(self.fleet_manager.traffic_manager.occupied_lanes)
        
        # Draw total robots
        text = self.legend_font.render(f"Total Robots: {total_robots}", True, self.WHITE)
        self.screen.blit(text, (self.legend_x + 10, y_offset))
        y_offset += 20
        
        # Draw waiting robots in red
        text = self.legend_font.render(f"Waiting: {waiting_robots}", True, self.RED)
        self.screen.blit(text, (self.legend_x + 10, y_offset))
        y_offset += 20
        
        # Draw occupied lanes in red
        text = self.legend_font.render(f"Occupied Lanes: {occupied_lanes}", True, self.RED)
        self.screen.blit(text, (self.legend_x + 10, y_offset))
        y_offset += 20
        
        # Draw robot status legend
        y_offset += 10
        statuses = [
            ("Idle", self.WHITE),
            ("Moving", self.GREEN),
            ("Waiting", self.RED),
            ("Charging", self.CYAN),
            ("Task Complete", self.YELLOW)
        ]
        
        for status, color in statuses:
            pygame.draw.circle(self.screen, color, (self.legend_x + 15, y_offset), 6)
            text = self.legend_font.render(status, True, self.WHITE)
            self.screen.blit(text, (self.legend_x + 30, y_offset - 6))
            y_offset += 20
            
    def draw_help(self):
        """
        Draw the help screen when 'H' is pressed.
        Shows a semi-transparent overlay with control instructions.
        """
        if not self.show_help:
            return
            
        # Create semi-transparent background
        help_surface = pygame.Surface((self.width, self.height))
        help_surface.fill(self.BLACK)
        help_surface.set_alpha(200)
        self.screen.blit(help_surface, (0, 0))
        
        # Draw help text
        y_offset = self.height // 2 - 60
        for text in self.help_text:
            text_surface = self.font.render(text, True, self.WHITE)
            text_rect = text_surface.get_rect(center=(self.width // 2, y_offset))
            self.screen.blit(text_surface, text_rect)
            y_offset += 40
            
    def draw(self):
        """
        Draw everything on the screen.
        This method:
        1. Clears the screen
        2. Draws all paths
        3. Draws all points
        4. Draws all robots
        5. Draws the selected robot indicator
        6. Draws action messages
        7. Draws the information panel
        8. Draws the help screen if active
        9. Draws the "Press H for help" text
        """
        self.screen.fill(self.BLACK)
        
        # Draw all paths
        for lane in self.fleet_manager.nav_graph.lanes:
            start_pos = self.fleet_manager.nav_graph.get_vertex_position(lane[0])
            end_pos = self.fleet_manager.nav_graph.get_vertex_position(lane[1])
            
            # Check if any robot is using this path
            is_occupied = False
            for robot in self.fleet_manager.robots.values():
                if robot.state == RobotState.MOVING:
                    current_lane = robot.get_current_lane()
                    if current_lane and (current_lane == lane or current_lane == (lane[1], lane[0])):
                        is_occupied = True
                        break
            
            self.draw_lane(start_pos, end_pos, is_occupied)
            
        # Draw all points
        for i, vertex in enumerate(self.fleet_manager.nav_graph.vertices):
            pos = (vertex[0], vertex[1])
            name = vertex[2].get('name', '')
            is_charger = vertex[2].get('is_charger', False)
            self.draw_vertex(pos, name, is_charger)
            
        # Draw all robots
        for robot in self.fleet_manager.robots.values():
            pos = robot.get_position(self.fleet_manager.nav_graph)
            self.draw_robot(robot, pos)
            
        # Draw selected robot indicator
        if self.fleet_manager.selected_robot:
            pos = self.fleet_manager.selected_robot.get_position(self.fleet_manager.nav_graph)
            screen_pos = self.world_to_screen(pos)
            pygame.draw.circle(self.screen, self.BLUE, screen_pos, 18, 3)
            
        # Draw action messages
        self.draw_action_messages()
        
        # Draw legend
        self.draw_legend()
        
        # Draw help screen if active
        self.draw_help()
        
        # Draw "Press H for help" text
        help_text = self.message_font.render("Press H for help", True, self.WHITE)
        self.screen.blit(help_text, (20, 20))
            
        pygame.display.flip()
        
    def handle_events(self) -> bool:
        """
        Handle all user input events.
        Returns False if the application should quit.
        
        This method handles:
        1. Window close button
        2. 'H' key for help screen
        3. Left click to create/select robots and assign tasks
        4. Right click to deselect robots
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    self.show_help = not self.show_help
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    world_pos = self.screen_to_world(event.pos)
                    
                    # Check if clicked on a robot
                    robot = self.fleet_manager.get_robot_at_position(world_pos)
                    if robot:
                        self.fleet_manager.select_robot(robot.robot_id)
                        self.add_action_message(f"Selected Robot {robot.robot_id}", self.BLUE)
                        continue
                        
                    # Check if clicked on a point
                    vertex = self.fleet_manager.get_vertex_at_position(world_pos)
                    if vertex is not None:
                        if self.fleet_manager.selected_robot:
                            # Assign task to selected robot
                            if self.fleet_manager.assign_task(vertex):
                                self.add_action_message(
                                    f"Assigned task to Robot {self.fleet_manager.selected_robot.robot_id}",
                                    self.GREEN
                                )
                                self.fleet_manager.deselect_robot()
                        else:
                            # Create new robot
                            try:
                                new_robot = self.fleet_manager.create_robot(vertex)
                                self.add_action_message(
                                    f"Created Robot {new_robot.robot_id}",
                                    self.YELLOW
                                )
                            except ValueError as e:
                                self.add_action_message(f"Error: {str(e)}", self.RED)
                                
                elif event.button == 3:  # Right click
                    if self.fleet_manager.selected_robot:
                        self.add_action_message(
                            f"Deselected Robot {self.fleet_manager.selected_robot.robot_id}",
                            self.GRAY
                        )
                    self.fleet_manager.deselect_robot()
                    
        return True
        
    def run(self):
        """Main GUI loop."""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            # Handle events
            running = self.handle_events()
            
            # Update fleet manager
            self.fleet_manager.update(1/60)  # Assuming 60 FPS
            
            # Draw everything
            self.draw()
            
            # Cap the frame rate
            clock.tick(60)
            
        pygame.quit()
        sys.exit() 