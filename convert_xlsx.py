import pandas as pd
import json
import re
import tkinter as tk
from tkinter import filedialog, messagebox
from collections import defaultdict

def get_group_key(name):
    match = re.match(r'^([a-zA-Z]+)[-_]?', str(name))
    return match.group(1) if match else name

def generate_nodesailor_json(xlsx_path, output_path):
    df = pd.read_excel(xlsx_path)

    expected_columns = ['name', 'VLAN_100', 'VLAN_200', 'VLAN_300', 'VLAN_400',
                        'remote_desktop_address', 'file_path', 'web_config_url']
    for col in expected_columns:
        if col not in df.columns:
            df[col] = ""

    df['group'] = df['name'].apply(get_group_key)

    # Layout planning
    screen_width = 1920 - 200  # padding
    screen_height = 1080 - 200
    max_per_row = 6
    x_spacing = screen_width // max_per_row
    y_spacing = 120

    json_nodes = []
    grouped = defaultdict(list)
    for _, row in df.iterrows():
        grouped[row['group']].append(row)

    y_index = 0
    for group, nodes in grouped.items():
        for x_index, row in enumerate(nodes):
            if x_index >= max_per_row:
                x_index = x_index % max_per_row
                y_index += 1

            node_json = {
                "name": row["name"],
                "VLAN_100": row["VLAN_100"],
                "VLAN_200": row["VLAN_200"],
                "VLAN_300": row["VLAN_300"],
                "VLAN_400": row["VLAN_400"],
                "remote_desktop_address": row["remote_desktop_address"],
                "file_path": row["file_path"],
                "web_config_url": row["web_config_url"],
                "x": x_index * x_spacing + 100,
                "y": y_index * y_spacing + 100
            }
            json_nodes.append(node_json)
        y_index += 1

    json_data = {
        "nodes": json_nodes,
        "connections": [],
        "vlan_labels": {
            "VLAN_100": "VLAN_100",
            "VLAN_200": "VLAN_200",
            "VLAN_300": "VLAN_300",
            "VLAN_400": "VLAN_400"
        },
        "stickynotes": []
    }

    with open(output_path, "w") as f:
        json.dump(json_data, f, indent=4)

def run_gui():
    root = tk.Tk()
    root.withdraw()

    xlsx_path = filedialog.askopenfilename(title="Select Excel File", filetypes=[("Excel Files", "*.xlsx")])
    if not xlsx_path:
        return

    output_path = filedialog.asksaveasfilename(title="Save JSON As", defaultextension=".json", filetypes=[("JSON Files", "*.json")])
    if not output_path:
        return

    try:
        generate_nodesailor_json(xlsx_path, output_path)
        messagebox.showinfo("Success", f"Exported NodeSailor JSON:\n{output_path}")

    except Exception as e:
        messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    run_gui()
