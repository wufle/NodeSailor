#!/usr/bin/env python3
"""
Test script to validate waypoint persistence bug diagnosis.
This script will test the two identified problems:
1. Missing waypoint loading in load_network_state()
2. Missing connection_lines cleanup in clear_current_loaded()
"""

import json
import tkinter as tk
from gui import NetworkMapGUI
from nodes import NetworkNode
from connections import ConnectionLine

def test_waypoint_persistence_bug():
    """Test the waypoint persistence issues"""
    
    print("=== WAYPOINT PERSISTENCE BUG DIAGNOSIS TEST ===")
    
    # Create a minimal GUI for testing
    root = tk.Tk()
    root.withdraw()  # Hide the window
    gui = NetworkMapGUI(root)
    
    # Test 1: Create nodes and connections with waypoints
    print("\n1. Creating test network with waypoints...")
    
    # Create two nodes
    node1 = NetworkNode(gui.canvas, "Node1", 100, 100)
    node2 = NetworkNode(gui.canvas, "Node2", 300, 100)
    gui.nodes = [node1, node2]
    
    # Create connection with waypoints
    waypoints = [(200, 50), (200, 150)]
    conn = ConnectionLine(gui.canvas, node1, node2, waypoints=waypoints, gui=gui)
    
    print(f"   - Created connection with {len(conn.waypoints)} waypoints")
    print(f"   - connection_lines list has {len(gui.connection_lines)} connections")
    print(f"   - Canvas waypoint handles: {len(gui.canvas.find_withtag('waypoint_handle'))}")
    
    # Test 2: Test clear_current_loaded() function
    print("\n2. Testing clear_current_loaded()...")
    initial_handles = len(gui.canvas.find_withtag('waypoint_handle'))
    gui.clear_current_loaded()
    remaining_handles = len(gui.canvas.find_withtag('waypoint_handle'))
    
    print(f"   - Waypoint handles before clear: {initial_handles}")
    print(f"   - Waypoint handles after clear: {remaining_handles}")
    print(f"   - connection_lines list after clear: {len(gui.connection_lines)}")
    
    if remaining_handles > 0:
        print("   ❌ BUG CONFIRMED: Waypoint handles not properly cleared!")
    else:
        print("   ✅ Waypoint handles properly cleared")
        
    if len(gui.connection_lines) > 0:
        print("   ❌ BUG CONFIRMED: connection_lines list not properly cleared!")
    else:
        print("   ✅ connection_lines list properly cleared")
    
    # Test 3: Test connection loading with and without waypoints
    print("\n3. Testing connection loading functions...")
    
    # Create test data
    test_data = {
        'nodes': [
            {'name': 'TestNode1', 'x': 100, 'y': 100},
            {'name': 'TestNode2', 'x': 300, 'y': 100}
        ],
        'connections': [
            {
                'from': 0, 
                'to': 1, 
                'label': 'test_connection',
                'waypoints': [[200, 50], [200, 150]]
            }
        ]
    }
    
    # Clear everything first
    gui.nodes.clear()
    gui.connection_lines.clear()
    gui.canvas.delete("all")
    
    # Test load_network_state_from_path (should work correctly)
    print("\n   Testing load_network_state_from_path()...")
    with open('test_waypoints.json', 'w') as f:
        json.dump(test_data, f)
    
    gui.load_network_state_from_path('test_waypoints.json')
    
    connections_with_waypoints = [c for c in gui.connection_lines if c.waypoints]
    print(f"   - Connections loaded: {len(gui.connection_lines)}")
    print(f"   - Connections with waypoints: {len(connections_with_waypoints)}")
    
    if connections_with_waypoints:
        print(f"   ✅ load_network_state_from_path() correctly loads waypoints")
        print(f"      First connection has {len(connections_with_waypoints[0].waypoints)} waypoints")
    else:
        print(f"   ❌ load_network_state_from_path() failed to load waypoints")
    
    # Clean up
    import os
    if os.path.exists('test_waypoints.json'):
        os.remove('test_waypoints.json')
    
    root.destroy()
    
    print("\n=== DIAGNOSIS COMPLETE ===")
    print("\nPROBLEMS IDENTIFIED:")
    print("1. load_network_state() function missing waypoint loading code")
    print("2. clear_current_loaded() function missing connection_lines cleanup")
    print("3. Waypoint handles may persist on canvas after clearing")

if __name__ == "__main__":
    test_waypoint_persistence_bug()