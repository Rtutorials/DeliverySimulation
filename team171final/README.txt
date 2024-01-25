Description:
The package is a simulation tool that models the movement and interactions of drivers, restaurants, and customers in a delivery network. It is built on top of popular Python packages and provides customizable parameters for adjusting the simulation to specific use cases. The simulation output includes dynamic visualizations and rolling statistics to provide insights into the delivery network's performance.

Installation:

To install and set up the simulation, first, ensure that Python 3.x installed on your system. Then install the required dependencies, including pandas, networkx, osmnx, matplotlib, and scipy. Next, download the project files, including simulation.py, agents.py, and utils.py. Once downloaded, navigate to the directory containing these files and run the installation command.


Execution:
To run the simulation, open the Main_notebook.ipynb notebook file and locate the parameters section. This section contains variables that control the simulation, such as the number of drivers, restaurants, and customers, the maximum order limit for drivers, and the moving speed of drivers across the network. The section also includes variables for enabling handoffs and setting the distance criteria for triggering a handoff. Once the parameters are set, run the main loop to start the simulation. The output includes a dynamic visualization of the drivers' movements, along with messages indicating when an event occurs, such as a pickup, delivery, or handoff. After the simulation run is complete, access the rolling statistics section to analyze the simulation's performance.
To run the D3 visualization, the simplest method is to use the built-in HTTP server module available in Python.
	1. Open a terminal or command prompt.
	2. Navigate to the directory containing your D3 visualization files.
	3. Run the following commands: Python 3.x: python -m http.server 8000
	4. Once the server is running, open your web browser and navigate to http://localhost:8000 to access your D3 visualizations. If you need to use a different port, replace 8000 with the desired port number in the command. The HTML will be under D3 in Q5, Q5.html. It processes a lot of data, so it may take a while to start up when you hit 'Start'. 
