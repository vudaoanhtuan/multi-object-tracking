# Desktop Application Design: Multi-Object Tracking (MOT) Visualization & Annotation Tool

## 1. Overview

This application is a desktop tool for visualizing and annotating datasets used in multi-object tracking (MOT). It enables users to:

* View annotated tracking results
* Manually create and edit tracking labels
* Automatically generate tracking labels from object detection outputs

The tool is designed for efficiency, usability, and scalability across large datasets.

---

## 2. Dataset Structure

Each dataset consists of multiple **samples**, where each sample is a directory with the following structure:

```
sample_<id>/
├── frames/
│   ├── 000000.jpeg
│   ├── 000001.jpeg
│   └── ...
├── object_detection/   (optional)
│   ├── 000000.txt
│   ├── 000001.txt
│   └── ...
└── mot_label/
    ├── 000000.txt
    ├── 000001.txt
    └── ...
```

### 2.1 Definitions

* **sample_id**: Unique identifier of a sample (e.g., `sample_123`)
* **frame_id**: Derived from filename (e.g., `000000`)

---

## 3. Data Formats

### 3.1 Frames

* Located in `frames/`
* Format: `.jpeg`
* Filename = frame ID

---

### 3.2 Object Detection (Optional)

* Located in `object_detection/`
* Each `.txt` file corresponds to a frame
* Each line represents one detected object:

```
x_min, y_min, x_max, y_max, x_camera, y_camera
```

**Fields:**

* `(x_min, y_min, x_max, y_max)`: Bounding box coordinates
* `(x_camera, y_camera)`: Object position in camera coordinate system

---

### 3.3 MOT Labels (Ground Truth)

* Located in `mot_label/`
* Each `.txt` file corresponds to a frame
* Each line represents one tracked object:

```
object_id, x_min, y_min, x_max, y_max
```

**Fields:**

* `object_id`: Integer ID representing object identity across frames
* Bounding box coordinates

---

## 4. Core Features

### 4.1 Annotation Mode

This mode allows users to create and edit MOT labels.

#### 4.1.1 Manual Annotation

For each frame:

* Draw bounding boxes
* Assign an `object_id`:

  * Select from existing IDs
  * Create new IDs for new objects

#### 4.1.2 Editing Tools

Users can:

* Select bounding boxes
* Move bounding boxes
* Resize bounding boxes
* Delete bounding boxes
* Change `object_id` of selected box

#### 4.1.3 Visual Aids

* Each `object_id` is displayed with a unique color
* Highlight selected bounding box
* Display object ID near bounding box

---

### 4.1.4 Auto-Labeling

If `object_detection/` exists:

* Run a simple tracking algorithm to generate initial MOT labels
* Output results into `mot_label/`

Possible tracking strategies:

* IoU-based matching across frames
* Nearest neighbor (distance in image or camera coordinates)
* Hungarian algorithm (optional advanced)

This is optional, skip it for now

---

### 4.1.5 Navigation & Interaction

* Frame navigation:

  * Next/previous frame (keyboard shortcuts)
* Zoom:

  * `Ctrl + Mouse Scroll` to zoom in/out
* Pan:

  * Click + drag (optional)

---

### 4.1.6 Save Mechanism

* Changes are **not auto-saved**
* After modification:

  * Save button is highlighted
* User must manually trigger save
* Save writes updated labels to `mot_label/`

---

### 4.1.7 Hotkeys (Recommended)

Support common shortcuts:

* `A`: Add bounding box
* `Delete`: Remove selected box
* `Ctrl + S`: Save
* `← / →`: Previous / Next frame
* `Ctrl + Scroll`: Zoom
* Number keys: Assign object ID (optional)

---

## 4.2 View Mode

This mode is read-only and used for visualization.

### Features:

* Display frames with bounding boxes from `mot_label/`
* Show object IDs with consistent colors
* Navigate frames
* No editing allowed

---

## 5. UI/UX Requirements

### 5.1 Layout

Suggested layout:

* Left panel: Sample & frame browser
* Center: Image canvas (main workspace)
* Right panel: Object list / properties
* Top bar: Controls (mode switch, save, auto-label)

---

### 5.2 Canvas Behavior

* Smooth rendering of images and overlays
* Real-time updates when editing
* Zoom centered on cursor
* Bounding boxes scale correctly with zoom

---

## 6. Functional Requirements Summary

| Feature             | Annotation Mode | View Mode |
| ------------------- | --------------- | --------- |
| Draw bounding boxes | ✅               | ❌         |
| Edit bounding boxes | ✅               | ❌         |
| Assign object IDs   | ✅               | ❌         |
| Auto-label          | ✅               | ❌         |
| Save labels         | ✅               | ❌         |
| View labels         | ✅               | ✅         |
| Zoom & navigation   | ✅               | ✅         |

---

## 7. Non-Functional Requirements

* Responsive UI for large datasets
* Efficient rendering for high-resolution frames
* Modular architecture (data handling, UI, tracking logic separated)

