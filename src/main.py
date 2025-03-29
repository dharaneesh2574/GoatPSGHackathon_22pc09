import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.models.nav_graph import NavGraph
from src.controllers.fleet_manager import FleetManager
from src.gui.fleet_gui import FleetGUI

def main():
    # Get the absolute path to the nav_graph.json file
    nav_graph_path = os.path.join(project_root, 'data', 'nav_graph_3.json')
    
    # Initialize components
    nav_graph = NavGraph(nav_graph_path)
    fleet_manager = FleetManager(nav_graph)
    gui = FleetGUI(fleet_manager)
    
    # Run the application
    gui.run()

if __name__ == "__main__":
    main() 