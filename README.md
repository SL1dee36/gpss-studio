# GPSS/H Studio

A lightweight, dedicated desktop IDE and simulation runner for Wolverine Software GPSS/H, built with Python and PySide6.
Runs the same way on Windows, Linux (Ubuntu, Arch, Fedora, ...) and macOS.

---

## Features

* **GPSS Column Formatting:** Split editor with a dedicated 2-character gutter for labels/comment tags and standard 2-space indentation for model statements.
* **One-Click Execution:** Compiles and executes simulation models directly through `gpssh.exe`.
* **Cross-Platform:** On Linux and macOS, `gpssh.exe` runs through a portable Wine that the app downloads and configures by itself.
* **Automatic Metric Extraction:** Parses simulation results directly from `.lis` files into a summary table (Clock, Facility utilization, Queue statistics).
* **Listing & Console Viewers:** Built-in inspection for compiler listings (`.lis`) and raw process execution streams (`STDOUT`/`STDERR`).
* **Editor Navigation:** Custom keybindings for indentation, line shifting, and quick label modification.

---

## Quick Start

1. Clone or download this repository.
2. Put your copy of `gpssh.exe` (Wolverine GPSS/H) into the repository folder. It is not included: the compiler is proprietary.
3. Run one command:

| OS | Command |
| --- | --- |
| **Linux / macOS** | `./run.sh` (or `sh run.sh`) |
| **Windows** | `run.bat` (or double-click it) |

That's it. The launcher takes care of everything else:

* installs [uv](https://docs.astral.sh/uv/) if it's missing, which provides Python and PySide6 in an isolated environment (nothing is installed into your system Python);
* **Linux:** installs `libxcb-cursor` via your package manager if Qt needs it (the only step that may ask for a sudo password);
* **Linux / macOS:** on first launch, downloads portable Wine (~100 MB, no root required) and prepares a private Wine prefix. This happens once and takes about a minute;
* **Apple Silicon Macs:** installs Rosetta 2 if it's missing (macOS asks for an administrator password).

Later launches start immediately, and each simulation run takes a fraction of a second.

### Where things are stored

Wine and its prefix live in the app data folder, so the repository folder stays clean:

* Linux: `~/.local/share/gpss-studio`
* macOS: `~/Library/Application Support/gpss-studio`
* Windows: nothing is downloaded; `gpssh.exe` runs natively.

Delete that folder to reset the Wine setup.

### Using your own Wine

Set `GPSS_WINE` to the path of a `wine` binary to skip the download, e.g. on unsupported platforms such as ARM Linux:

```bash
GPSS_WINE=/usr/bin/wine ./run.sh
```

### Manual run (without the launcher)

Requires Python 3.9+:

```bash
pip install PySide6
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

During simulation runs, these files are generated in the application directory (all git-ignored):

* `model.gps`: Generated GPSS/H input source code.
* `model.lis`: Output listing created by `gpssh.exe`.
* `gpssh.ini`: Settings file created by `gpssh.exe` on its first run.

---

## Model Syntax Guidelines

* **Do not use `SIMULATE`:** Modern GPSS/H does not require the legacy `SIMULATE` card; starting directly with blocks like `GENERATE` prevents `ERROR 4`.
* **Termination:** Always terminate the simulation run using `START [count]` followed by `END`.
