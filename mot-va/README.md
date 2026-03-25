# MOT Visualization & Annotation

A PyQt6-based desktop application for visualizing and annotating Multi-Object Tracking (MOT) datasets. It provides a user-friendly interface to navigate frames, draw bounding boxes, assign object IDs, and seamlessly save annotations.

## Prerequisites

- Python 3.11+
- PyQt6 >= 6.6
- ruff (for linting)

## Installation & Setup

1. **Create Virtual Environment and Install Dependencies:**
   A standard `Makefile` is provided to streamline the setup. Run the following command in the project root:
   ```bash
   make install
   ```

2. **Run the Application:**
   Start the application with:
   ```bash
   make run
   ```

## User Interface Overview

The main window is divided into several panels:

- **Main Toolbar (Top):** Contains quick actions for opening datasets, toggling Edit/View mode, zooming, frame navigation, toggling Auto Save, and manually saving or discarding changes.
- **Sample Browser (Left Sidebar):** A panel used to browse through the loaded dataset, showing different samples and frames.
- **Canvas (Center):** The main display area where the current frame image is rendered. This is where you draw, resize, and interact with bounding boxes.
- **Object List (Right Side Panel - inside Sample Browser):** Displays a list of all bounding boxes in the current frame, along with their assigned Object IDs and colors. It also includes buttons to change a bounding box's ID or delete it.

## Features & Usage

### 1. Opening a Dataset
- Click the **Open...** button on the toolbar to select a dataset directory containing your images and annotations.

### 2. View vs. Edit Mode
- Use the **Edit Mode** / **View Mode** toggle button in the toolbar to switch states.
- In **View Mode**, you can only navigate and inspect frames and bounding boxes without accidentally modifying them.
- In **Edit Mode**, you can draw new bounding boxes, resize them, delete them, and change object IDs.

### 3. Drawing and Managing Bounding Boxes
- **Draw Mode:** Click the **Draw (A)** button on the toolbar or press `A` on your keyboard to enter draw mode. Your cursor will turn into a crosshair. Click and drag on the canvas to draw a new bounding box. Press `Escape` to exit draw mode and return to standard interaction.
- **Select:** Click any bounding box on the canvas to select it. The corresponding ID will also be highlighted in the Object List panel.
- **Resize/Move:** Click and drag the edges/corners or the body of an existing bounding box to adjust its size and position.
- **Change ID:** Double-click on a bounding box on the canvas, or select it and click **Change ID** in the Object List panel, to assign a new or existing Object ID.
- **Delete:** Select a bounding box and press the `Delete` or `Backspace` key, or click **Delete** in the Object List panel, to remove it entirely.

### 4. Navigation & Zoom
- **Next/Previous Frame:** Click the `<` and `>` buttons on the toolbar, or use the `Left Arrow` and `Right Arrow` keys to navigate through the frames of the current sample.
- **Zoom In/Out:** Use the **Zoom In** and **Zoom Out** buttons, or use the keyboard shortcuts (`Ctrl++`, `Ctrl+-`), or hold `Ctrl` and scroll with your mouse wheel. You can click and drag the canvas to pan around when zoomed in.

### 5. Auto Save & Manual Saving
- **Auto Save:** By default, Auto Save is **On**. When enabled, any changes made to bounding boxes will be automatically saved whenever you switch to a different frame. You can toggle this feature via the **Auto Save: On/Off** button in the toolbar.
- **Manual Save/Discard:** If Auto Save is toggled off, the **Save** and **Discard** buttons will become active whenever there are unsaved modifications in the current frame. Be sure to save your changes before navigating away to avoid losing work!

## Keyboard Shortcuts Summary

| Action | Shortcut (Windows/Linux) | Shortcut (macOS) |
| --- | --- | --- |
| **Save Changes** | `Ctrl + S` | `Cmd + S` |
| **Zoom In** | `Ctrl + +` | `Cmd + +` |
| **Zoom Out** | `Ctrl + -` | `Cmd + -` |
| **Previous Frame** | `Left Arrow` | `Left Arrow` |
| **Next Frame** | `Right Arrow` | `Right Arrow` |
| **Enter Draw Mode** | `A` | `A` |
| **Exit Draw Mode** | `Escape` | `Escape` |
| **Delete Selected Box** | `Delete` | `Delete` / `Backspace` |

---
*Happy Annotating!*
