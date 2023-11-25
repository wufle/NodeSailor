# NodeSailor

NodeSailor is a basic network topology mapping, configuration and testing tool.  

I know next to nothing about network configuration or Python - this tool begun as a project created in order to better understand a unique network installation, and at the same time, learn how to write some Python.

It has largely been written copy/pasting ChatGPT prompts!    


**Installation Instrucitons:**

A prepackaged executable can be found in the releases section - https://github.com/wufle/NodeSailor/releases.  Simply download and run the NodeSailor.exe

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
  

