# NodeSailor

NodeSailor is a basic network topology mapping, configuration and testing tool.  It has largely been written by copy/pasting ChatGPT prompts, as I know next to nothing about network configuration or Python.  

*They took our jerbs!*

This project was created in order to better understand a certain, unique network installation and at the same time, learn how to write some Python.  It has evolved in to something that will be useful for future maintenance and testing (for me at least anyway!)

 ![image](https://github.com/wufle/NodeSailor/assets/121041163/c6629eee-93f7-4306-a2ce-06756320e175)


**Operation Instructions**

Networks are manually configured by the user when in "Configuration Mode". I've included a basic example config, 'example network.json'

In Operator mode, the user can perform basic network testing functions via a simple GUI. It is possible to quickly ascertain network status and access other common admin functions, like Remote desktop, File Explorer, Web browser.

Keyboard Shortcuts and Functions:
        
*Operator Mode:*
- 'F1' for help
- Left click on Node: Ping the node! Node will change colour depending on response, Green is good, Yellow means good on some Vlans (if configured), Red for no response.
- Right Click on Node: Open context menu for other node-specific operations
- 'Who am I?': Identify and highlight the node where this program is running
- 'Ping All': Ping all nodes and update their status
- 'Clear Status': Reset the status of all nodes
- Radio buttons for displaying/hiding selected Vlans

        
*Configuration Mode:*
- Double Left Click: Create a node
- Left click drag Node: Move node
- Shift + Double Left Click: Create a sticky note
- Shift left click drag to move sticky notes
- Middle Click: Create a connection between nodes
- Shift + Middle Click: Remove a connection
- Right Click on Node: Open context menu for additional options (Edit, Delete, Remote desktop, File Explorer, Web browser)
- 'Save': Save the current network state
- 'Load': Load a saved network state
  
**Installation Instructions:**

A prepackaged executable can be found in the releases section - https://github.com/wufle/NodeSailor/releases.  Simply download the latest release and run NodeSailor.exe

If you would instead like to run the project from the source, run through the steps below to setup a virtual python environment:

1. Create the Virtual Environment

Opent a terminal and run the command:

`python -m venv '.\NodeSailor'` <-- clone the project repository to this filepath

2. Activate the Virtual Environment

`cd '.\NodeSailor\'`

`.\Scripts\activate`

3. Install Packages While the Virtual Environment is Active
With the virtual environment active, you can install packages using pip. To install all required packages, run:

`pip install -r requirements.txt`

**Known bugs/problems:**
- Pan and zoom funcitonality messes with the alignment of cursor and nodes

**Future plans:**
* Colour scheme options
* Ping only selected networks/vlans
* New network create to open prompt to set network names
* User created background image for networks
* Codebase cleanup
* Make the help page pretty
* Node/cable list with search functionality
  

