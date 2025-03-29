# Fleet Management System

A visually intuitive and interactive Fleet Management System using Python Pygame, capable of managing multiple robots simultaneously navigating through an environment. The system features real-time visualization, collision avoidance, and dynamic task assignment.

## Features

1. **Visual Representation**
   - Environment visualization with vertices and lanes
   - Interactive vertex display with names and intersections
   - Real-time robot visualization with status indicators
   - Occupied lane highlighting

2. **Robot Management**
   - Dynamic robot spawning at vertices
   - Unique robot identification and color coding
   - Real-time status visualization (moving, waiting, charging, task complete)

3. **Task Assignment**
   - Interactive task assignment through GUI
   - Visual path planning and execution
   - Real-time task status updates

4. **Traffic Management**
   - Collision avoidance system
   - Lane occupancy tracking
   - Queue management for shared resources

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fleet-management-robots
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python src/main.py
```

### GUI Controls

- **Left Click on Vertex**: 
  - If no robot is selected: Creates a new robot at the clicked vertex
  - If a robot is selected: Assigns the clicked vertex as the destination

- **Left Click on Robot**: Selects the robot for task assignment

- **Right Click**: Cancels the current robot selection

### Visual Indicators

- **Robots**: 
  - Colored circles with unique IDs
  - Status ring color indicates current state:
    - White: Idle
    - Green: Moving
    - Red: Waiting
    - Cyan: Charging
    - Yellow: Task Complete

- **Vertices**:
  - White circles with names
  - Green ring indicates charging station

- **Lanes**:
  - Gray: Available
  - Red: Occupied

## Project Structure

```
fleet_management_system/
├── data/
│   └── nav_graph.json
├── src/
│   ├── models/
│   │   ├── nav_graph.py
│   │   └── robot.py
│   ├── controllers/
│   │   ├── fleet_manager.py
│   │   └── traffic_manager.py
│   ├── gui/
│   │   └── fleet_gui.py
│   └── main.py
├── requirements.txt
└── README.md
```

## Dependencies

- Python 3.7+
- Pygame 2.5.2
- NumPy 1.24.3

## License

This project is licensed under the MIT License - see the LICENSE file for details. 