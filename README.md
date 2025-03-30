# Fleet Management System

## Description
The Fleet Management System is a simulation application designed to manage and monitor a fleet of robots navigating through a defined environment. The system allows for the creation of robots, task assignment, and real-time visualization of robot movements and lane occupancy.

## Features
- Create and manage multiple robots.
- Assign tasks to robots and visualize their paths.
- Real-time updates on robot states and lane occupancy.
- Customizable navigation graph for different environments.

## Demo Link : https://drive.google.com/file/d/15l8hko1wyE_VbzdxZncONyGQEJ_UllrD/view?usp=sharing

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/dharaneesh2574/GoatPSGHackathon_22pc09
   cd GoatPSGHackathon_22pc09
   ```

2. **Install dependencies**:
   Make sure you have Python 3.x installed. You may need to install the required packages. You can do this using pip:
   ```bash
   pip install pygame
   ```

3. **Prepare the data**:
   Place your navigation graph JSON files in the `data` directory. The application is designed to work with any dataset that follows the expected structure.

## Running the Application

1. **Update the dataset**:
   To use a different dataset, update the path to your JSON file in `main.py`:
   ```python
   nav_graph_path = os.path.join(project_root, 'data', 'nav_graph_1.json') 
   ```
   you can also use nav_graph_2.json or nav_graph_3.json

2. **Run the application**:
   Execute the following command in your terminal:
   ```bash
   python src/main.py
   ```

3. **Interact with the GUI**:
   - Left Click on a vertex to create a robot.
   - Left Click on a robot to select it.
   - Left Click on a vertex while a robot is selected to assign a task.
   - Right Click to deselect a robot.
   - Press 'H' for help and to see the controls.

   ## Images
  
**nav_graph_2.json**
![Screenshot 2025-03-30 181239](https://github.com/user-attachments/assets/39179a08-2a77-43cb-9483-e055966e0c94)

**nav_graph_1.json**
![image](https://github.com/user-attachments/assets/bffe9902-f06a-4085-a1ed-9b34f22f341b)

**nav_graph_3.json**
![image](https://github.com/user-attachments/assets/785bd971-44fe-4bca-986a-7c71d0b19b9d)









