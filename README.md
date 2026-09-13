# GPSS/H Studio

A lightweight, dedicated desktop IDE and simulation runner for Wolverine Software GPSS/H, built with Python and PySide6.

---

## Features

* **GPSS Column Formatting:** Split editor with a dedicated 2-character gutter for labels/comment tags and standard 2-space indentation for model statements.
* **One-Click Execution:** Compiles and executes simulation models directly through `gpssh.exe`.
* **Automatic Metric Extraction:** Parses simulation results directly from `.lis` files into a summary table (Clock, Facility utilization, Queue statistics).
* **Listing & Console Viewers:** Built-in inspection for compiler listings (`.lis`) and raw process execution streams (`STDOUT`/`STDERR`).
* **Editor Navigation:** Custom keybindings for indentation, line shifting, and quick label modification.

---

## Requirements

* **Python:** Version 3.8 or higher
* **Dependencies:** `PySide6`
* **Compiler:** `gpssh.exe` (Wolverine GPSS/H executable)

---

## Installation & Setup

1. Install PySide6:
```bash
pip install PySide6
```
2. Place the Python script into a dedicated directory.
3. Place `gpssh.exe` into the **exact same directory** as the script.
4. Run the application:
```bash
python gpss-studio.py
```



---

## Workspace Layout

* **Left Pane (Editor):**
* **Label Gutter (Left):** Stores line labels or `*` for comments. Double-click or press `F2` to edit.
* **Code Editor (Right):** Write model statements without worrying about leading column spacing; the app automatically formats statements into column 3 on execution.


* **Right Pane (Tabs):**
* **Summary Report:** Key performance metrics extracted automatically (Absolute Clock, Facilities, Queues).
* **Full Listing (.lis):** GPSS/H compilation report and statistical tables.
* **Console Output:** Raw execution stdout and stderr messages.



---

## Keyboard Shortcuts

| Shortcut | Action |
| --- | --- |
| **F5** | Run simulation |
| **Home** / **Shift + Home** | Smart Home: Toggles between first non-whitespace character and column 0 |
| **Tab** / **Shift + Tab** | Indent / Unindent selected block or line (2 spaces) |
| **Alt + ↑** / **Alt + ↓** | Move current line up or down |
| **Ctrl + D** | Duplicate current line |
| **Ctrl + /** | Toggle comment flag (`*`) in the label column |
| **F2** | Edit the label/comment tag of the current line |
| **Ctrl + G** | Jump to line dialog |
| **Ctrl + 1** | Switch to **Summary Report** tab |
| **Ctrl + 2** | Switch to **Full Listing (.lis)** tab |
| **Ctrl + 3** | Switch to **Console Output** tab |

---

## Generated Files

During simulation runs, two temporary files are generated in the application directory:

* `model.gps`: Generated GPSS/H input source code.
* `model.lis`: Output listing created by `gpssh.exe`.

---

## Model Syntax Guidelines

* **Do not use `SIMULATE`:** Modern GPSS/H does not require the legacy `SIMULATE` card; starting directly with blocks like `GENERATE` prevents `ERROR 4`.
* **Termination:** Always terminate the simulation run using `START [count]` followed by `END`.
