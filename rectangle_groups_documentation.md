# Rectangle Groups in NodeSailor

## 1. Overview of the Rectangle Groups Feature

### What are Rectangle Groups?

Rectangle Groups are a visual organization feature in NodeSailor that allow you to group related network nodes together. By drawing rectangles around sets of nodes, you can create logical groupings that help clarify your network topology and improve the readability of complex network maps.

Rectangle Groups are particularly useful for:
- Organizing nodes by department or business unit
- Grouping nodes by physical location
- Highlighting nodes that serve a common function
- Creating visual separation between different network segments

### Visual Appearance

Rectangle Groups are designed to be visually distinct while not interfering with the nodes and connections they contain:
- Semi-transparent colored rectangles with a stippled pattern
- Colored borders that help distinguish between different groups
- Group names displayed in the top-left corner of each rectangle
- Always positioned behind nodes and connections to avoid obscuring important network elements

### Visibility and Editing

- Rectangle Groups are visible in both Configuration and Operator modes, providing consistent visual organization across all views of your network
- Groups can only be created and edited when in Configuration mode with the Groups feature active
- Once created, groups persist when switching between modes and when saving/loading network configurations

## 2. How to Use Rectangle Groups

### Creating Rectangle Groups

1. Switch to Configuration mode by clicking the "Configuration" button in the toolbar
2. Click the "Groups" button to activate Groups mode (the button will appear pressed/sunken when active)
3. Click and drag on the canvas to draw a rectangle:
   - The starting point will be where you first click
   - As you drag, a dashed outline will show the current size and position
   - Release the mouse button to complete the rectangle
4. After releasing the mouse button, the Group Editor window will automatically open if the rectangle is large enough (minimum size requirements apply)
5. Enter a name for the group and select a color (or use the default)
6. Click "Save" to create the group

### Editing Existing Rectangle Groups

1. Ensure you are in Configuration mode with Groups mode active (click "Groups" button)
2. Click on an existing rectangle group to select it (the border will highlight to indicate selection)
3. The Group Editor window will open automatically, allowing you to:
   - Change the group name by editing the text in the "Group Name" field
   - Change the group color by clicking the "Choose Color" button and selecting a new color
4. Click "Save" to apply your changes

### Deleting Rectangle Groups

1. Ensure you are in Configuration mode with Groups mode active
2. Click on the rectangle group you wish to delete
3. In the Group Editor window that appears, click the "Delete" button
4. The group will be removed immediately

## 3. Tips and Best Practices

### Effective Use of Rectangle Groups

- **Use consistent color coding**: Establish a color scheme where similar types of groups use similar colors (e.g., all departments could use shades of blue, while locations use shades of green)
- **Keep group names concise**: Short, descriptive names improve readability
- **Avoid overcrowding**: Don't create too many overlapping groups, as this can make the network map harder to read
- **Group logically**: Create groups that reflect real-world relationships between nodes
- **Use groups for documentation**: Groups can serve as visual documentation of your network's logical structure

### Limitations and Considerations

- Rectangle Groups are purely visual and don't affect the functionality of nodes or connections
- Groups will be drawn behind all nodes and connections, so they won't interfere with network operations
- Very small rectangles (less than approximately 10x10 pixels) won't be created
- When moving nodes, you may need to manually reorganize your groups if nodes are moved outside their group boundaries
- Groups are saved with your network configuration, so they will persist between sessions
- While groups are visible in Operator mode, remember that they can only be created or modified in Configuration mode