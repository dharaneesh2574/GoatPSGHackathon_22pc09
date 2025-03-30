import pygame
import sys
from typing import Tuple, Optional
from src.controllers.fleet_manager import FleetManager
from src.models.nav_graph import NavGraph
from src.models.robot import RobotState

class FleetGUI:
    def __init__(self, fleet_manager: FleetManager, width: int = 1200, height: int = 800):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Fleet Management System")
        
        self.fleet_manager = fleet_manager
        self.width = width
        self.height = height
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (128, 128, 128)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
        self.YELLOW = (255, 255, 0)
        self.CYAN = (0, 255, 255)
        
        # Fonts
        self.font = pygame.font.Font(None, 36)  # Larger font for vertex names
        self.message_font = pygame.font.Font(None, 24)  # Font for action messages
        self.legend_font = pygame.font.Font(None, 20)  # Font for legend
        
        # Calculate scale and offset to center the graph
        self._calculate_view_transform()
        
        # Action message system
        self.action_messages = []
        self.message_duration = 3.0  # seconds
        self.message_start_time = 0
        
        # Legend panel dimensions
        self.legend_width = 250
        self.legend_height = 200
        self.legend_x = width - self.legend_width - 20
        self.legend_y = 20
        
        # Help screen
        self.show_help = False
        self.help_text = [
            "Left Click Vertex: Create Robot",
            "Left Click Robot: Select Robot",
            "Left Click Vertex + Selected Robot: Assign Task",
            "Right Click: Deselect Robot, H: Toggle Help"
        ]
        
    def _calculate_view_transform(self):
        """Calculate the scale and offset to center the graph in the window."""
        # Find the bounds of the graph
        min_x = min(v[0] for v in self.fleet_manager.nav_graph.vertices)
        max_x = max(v[0] for v in self.fleet_manager.nav_graph.vertices)
        min_y = min(v[1] for v in self.fleet_manager.nav_graph.vertices)
        max_y = max(v[1] for v in self.fleet_manager.nav_graph.vertices)
        
        # Calculate graph dimensions
        graph_width = max_x - min_x
        graph_height = max_y - min_y
        
        # Calculate scale to fit graph in window with padding
        padding = 150  # Increased padding
        scale_x = (self.width - 2 * padding) / graph_width
        scale_y = (self.height - 2 * padding) / graph_height
        self.scale = min(scale_x, scale_y)
        
        # Calculate offset to center the graph
        self.offset_x = self.width / 2 - (min_x + max_x) * self.scale / 2
        self.offset_y = self.height / 2 - (min_y + max_y) * self.scale / 2
        
    def world_to_screen(self, pos: Tuple[float, float]) -> Tuple[int, int]:
        """Convert world coordinates to screen coordinates."""
        return (
            int(pos[0] * self.scale + self.offset_x),
            int(pos[1] * self.scale + self.offset_y)
        )
        
    def screen_to_world(self, pos: Tuple[int, int]) -> Tuple[float, float]:
        """Convert screen coordinates to world coordinates."""
        return (
            (pos[0] - self.offset_x) / self.scale,
            (pos[1] - self.offset_y) / self.scale
        )
        
    def add_action_message(self, message: str, color: Tuple[int, int, int] = None):
        """Add a new action message to display."""
        if color is None:
            color = self.WHITE
        self.action_messages.append({
            'text': message,
            'color': color,
            'start_time': pygame.time.get_ticks() / 1000.0
        })
        
    def draw_vertex(self, pos: Tuple[float, float], name: str, is_charger: bool = False):
        """Draw a vertex with its name and charger status."""
        screen_pos = self.world_to_screen(pos)
        
        # Draw vertex circle (larger)
        pygame.draw.circle(self.screen, self.WHITE, screen_pos, 8)
        
        # Draw charger indicator if applicable
        if is_charger:
            pygame.draw.circle(self.screen, self.GREEN, screen_pos, 10, 3)
            
        # Draw vertex name
        if name:
            text = self.font.render(name, True, self.WHITE)
            text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - 20))
            self.screen.blit(text, text_rect)
            
    def draw_lane(self, start: Tuple[float, float], end: Tuple[float, float], is_occupied: bool = False):
        """Draw a lane between two vertices."""
        start_pos = self.world_to_screen(start)
        end_pos = self.world_to_screen(end)
        
        # Draw lane line (thicker)
        if is_occupied:
            # Draw red background for occupied lanes
            pygame.draw.line(self.screen, self.RED, start_pos, end_pos, 6)
            # Draw white line on top for better visibility
            pygame.draw.line(self.screen, self.WHITE, start_pos, end_pos, 2)
        else:
            # Draw gray line for available lanes
            pygame.draw.line(self.screen, self.GRAY, start_pos, end_pos, 4)
            
    def draw_robot(self, robot, pos: Tuple[float, float]):
        """Draw a robot with its ID and status."""
        screen_pos = self.world_to_screen(pos)
        
        # Draw robot circle (larger)
        pygame.draw.circle(self.screen, robot.color, screen_pos, 12)
        
        # Draw robot ID
        text = self.font.render(str(robot.robot_id), True, self.WHITE)
        text_rect = text.get_rect(center=screen_pos)
        self.screen.blit(text, text_rect)
        
        # Draw status indicator (larger)
        status_color = {
            RobotState.IDLE: self.WHITE,
            RobotState.MOVING: self.GREEN,
            RobotState.WAITING: self.RED,
            RobotState.CHARGING: self.CYAN,
            RobotState.TASK_COMPLETE: self.YELLOW
        }.get(robot.state, self.WHITE)
        
        pygame.draw.circle(self.screen, status_color, screen_pos, 15, 3)
        
    def draw_action_messages(self):
        """Draw action messages in the top-right corner."""
        current_time = pygame.time.get_ticks() / 1000.0
        y_offset = 20
        
        # Filter out expired messages
        self.action_messages = [msg for msg in self.action_messages 
                              if current_time - msg['start_time'] < self.message_duration]
        
        # Draw messages from bottom to top
        for msg in reversed(self.action_messages):
            text = self.message_font.render(msg['text'], True, msg['color'])
            text_rect = text.get_rect()
            text_rect.topright = (self.width - 20, y_offset)
            self.screen.blit(text, text_rect)
            y_offset += 30
            
    def draw_legend(self):
        """Draw the legend panel with robot information and statistics."""
        # Draw legend background
        legend_surface = pygame.Surface((self.legend_width, self.legend_height))
        legend_surface.fill(self.BLACK)
        legend_surface.set_alpha(200)  # Semi-transparent
        self.screen.blit(legend_surface, (self.legend_x, self.legend_y))
        
        # Draw legend border
        pygame.draw.rect(self.screen, self.WHITE, 
                        (self.legend_x, self.legend_y, self.legend_width, self.legend_height), 2)
        
        # Draw title
        title = self.legend_font.render("Fleet Status", True, self.WHITE)
        self.screen.blit(title, (self.legend_x + 10, self.legend_y + 10))
        
        # Draw robot count
        robot_count = self.legend_font.render(f"Total Robots: {len(self.fleet_manager.robots)}", True, self.WHITE)
        self.screen.blit(robot_count, (self.legend_x + 10, self.legend_y + 40))
        
        # Count waiting robots
        waiting_count = sum(1 for robot in self.fleet_manager.robots.values() 
                          if robot.state == RobotState.WAITING)
        waiting_text = self.legend_font.render(f"Waiting Robots: {waiting_count}", True, self.RED)
        self.screen.blit(waiting_text, (self.legend_x + 10, self.legend_y + 60))
        
        # Count occupied lanes
        occupied_lanes = len(self.fleet_manager.traffic_manager.get_occupied_lanes())
        lanes_text = self.legend_font.render(f"Occupied Lanes: {occupied_lanes}", True, self.RED)
        self.screen.blit(lanes_text, (self.legend_x + 10, self.legend_y + 80))
        
        # Draw robot status legend
        y_offset = self.legend_y + 110
        status_legend = [
            (self.WHITE, "Idle"),
            (self.GREEN, "Moving"),
            (self.RED, "Waiting"),
            (self.CYAN, "Charging"),
            (self.YELLOW, "Task Complete")
        ]
        
        for color, status in status_legend:
            # Draw color indicator
            pygame.draw.circle(self.screen, color, (self.legend_x + 15, y_offset), 6)
            # Draw status text
            text = self.legend_font.render(status, True, self.WHITE)
            self.screen.blit(text, (self.legend_x + 30, y_offset - 6))
            y_offset += 20
            
    def draw_help(self):
        """Draw the help screen."""
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
        """Draw the entire GUI."""
        self.screen.fill(self.BLACK)
        
        # Draw all lanes
        for lane in self.fleet_manager.nav_graph.lanes:
            start_pos = self.fleet_manager.nav_graph.get_vertex_position(lane[0])
            end_pos = self.fleet_manager.nav_graph.get_vertex_position(lane[1])
            
            # Check if any robot is currently using this lane
            is_occupied = False
            for robot in self.fleet_manager.robots.values():
                if robot.state == RobotState.MOVING:
                    current_lane = robot.get_current_lane()
                    if current_lane and (current_lane == lane or current_lane == (lane[1], lane[0])):
                        is_occupied = True
                        break
            
            self.draw_lane(start_pos, end_pos, is_occupied)
            
        # Draw all vertices
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
        """Handle Pygame events. Returns False if the application should quit."""
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
                        
                    # Check if clicked on a vertex
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