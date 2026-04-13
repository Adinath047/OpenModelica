# OpenModelica Desktop Launcher

This repository contains a Python desktop application built with PyQt6 for
launching an OpenModelica-generated simulation executable. The app lets a user:

- browse for the compiled executable
- enter integer `start time` and `stop time` values
- run the executable with OpenModelica override flags
- review the command preview and execution output inside the GUI

The project is structured to satisfy the screening requirements while keeping
the logic modular, testable, and easy to review.

## Why This App Exists

OpenModelica can generate a standalone simulation executable for a model such as
`TwoConnectedTanks`. That executable still needs runtime arguments when it is
launched. This project provides a simple desktop front end so a user can run the
generated model without remembering the exact command-line syntax every time.

## Features

- PyQt6 desktop interface
- input validation for the required condition `0 <= start time < stop time < 5`
- object-oriented design with GUI and validation logic separated
- command generation using the OpenModelica `-override` simulation flag
- non-blocking execution using Qt's process API, so the window stays responsive
- basic automated tests for non-GUI logic
- repository layout prepared for bundling the generated model executable

## Repository Structure

```text
.
├── main.py
├── model_runtime/
│   └── README.md
├── openmodelica_launcher/
│   ├── __init__.py
│   ├── core.py
│   └── gui.py
├── pyproject.toml
├── requirements.txt
├── scripts/
│   └── package_openmodelica_model.mos
└── tests/
    └── test_core.py
```

## Application Workflow

1. Click `Browse` and select the compiled `TwoConnectedTanks` executable.
2. Enter the start time and stop time as integers.
3. Click `Run Simulation`.
4. The application launches the executable with an argument of the form:

```text
-override=startTime=<start>,stopTime=<stop>
```

5. The command preview and process output are shown in the window.

## What You Can Do With It

- run a compiled OpenModelica model from a desktop UI
- avoid manually typing `-override=startTime=...,stopTime=...`
- validate time inputs before starting the simulation
- inspect the simulation output directly in the app
- reuse the same launcher for other compatible OpenModelica-generated executables

## Validation Rules

The launcher enforces the test condition required in the task:

- `start time >= 0`
- `stop time < 5`
- `start time < stop time`

If validation fails, the application shows an error dialog and does not launch
the executable.

## Setup Instructions

### 1. Install Python dependencies

Create a virtual environment if desired, then install the GUI dependency:

```bash
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

This project now targets Python 3.10 or newer.

If you also want the development test dependency, install:

```bash
./.venv/bin/python -m pip install -e ".[dev]"
```

### 2. Run the desktop app

```bash
./.venv/bin/python main.py
```

### 3. Run the tests

```bash
./.venv/bin/python -m unittest discover -s tests -v
```

### 4. Optional local demo

If you want to test the GUI before compiling the real OpenModelica model, make
the demo script executable and select it from the app:

```bash
chmod +x model_runtime/demo_two_connected_tanks.sh
```

It accepts the same `-override=...` argument shape and prints the received
values back to the output panel.

On Windows, you can use `model_runtime/demo_two_connected_tanks.bat` for the
same purpose.

## Building the OpenModelica Executable

The environment used to prepare this repository did not have OpenModelica
installed, so the repository includes the exact packaging scaffold and the
script needed for the build step. On the machine where OpenModelica is
installed, complete the following:

1. Download the model package that contains `TwoConnectedTanks`.
2. Place the extracted package beside
   `scripts/package_openmodelica_model.mos`, or update the `loadFile(...)`
   path inside the `.mos` script.
3. Run:

```bash
omc scripts/package_openmodelica_model.mos
```

4. OpenModelica should generate the `TwoConnectedTanks` executable and
   companion runtime files.
5. Copy all generated runtime artifacts into the `model_runtime/` directory.

## Linux Build Guide

This section is based on the official OpenModelica Linux download page and the
official scripting documentation.

1. Install OpenModelica on Ubuntu or Debian:

```bash
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg
curl -fsSL https://build.openmodelica.org/apt/openmodelica.asc | \
  sudo gpg --dearmor -o /usr/share/keyrings/openmodelica-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/openmodelica-keyring.gpg] \
  https://build.openmodelica.org/apt \
  $(cat /etc/os-release | grep \"\\(UBUNTU\\|DEBIAN\\|VERSION\\)_CODENAME\" | sort | cut -d= -f 2 | head -1) \
  stable" | sudo tee /etc/apt/sources.list.d/openmodelica.list
sudo apt update
sudo apt install openmodelica
```

2. Confirm the compiler is available:

```bash
omc --version
```

3. Download the model package that contains `TwoConnectedTanks`.
4. Update `scripts/package_openmodelica_model.mos` if the package path differs.
5. Run:

```bash
omc scripts/package_openmodelica_model.mos
```

6. Copy the produced `TwoConnectedTanks` executable and nearby generated files
   into `model_runtime/`.
7. Start the launcher and select the copied executable.

## Windows Build Guide

This section is based on the official OpenModelica Windows download page and
the official user guide.

1. Download the current Windows release installer from the official OpenModelica
   Windows downloads page.
2. Install OpenModelica and keep OMEdit selected during installation.
3. Open `OMEdit`.
4. Load the downloaded model package that contains `TwoConnectedTanks`.
5. Build or simulate `TwoConnectedTanks` so OpenModelica generates the
   executable and runtime files.
6. You can also run the `.mos` script from the compiler directly if `omc.exe`
   is on your `PATH`, or by using the installed OpenModelica `build\\bin\\omc.exe`.
7. Copy the generated `.exe` and all companion files into `model_runtime\\`.
8. Run the Python launcher:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python main.py
```

## Running the Generated Executable Manually

After compilation, the executable can be launched from the terminal like this:

```bash
./TwoConnectedTanks -override=startTime=0,stopTime=4
```

On Windows, the executable would typically be:

```powershell
.\TwoConnectedTanks.exe -override=startTime=0,stopTime=4
```

## OOP Design Notes

- `SimulationRequest` in `openmodelica_launcher/core.py` is a data class that
  represents a validated launch request.
- `LauncherWindow` in `openmodelica_launcher/gui.py` manages the desktop UI and
  user interactions.
- Validation and command construction are kept outside the widget layer to make
  the code easier to test and maintain.

## Submission Notes

Before sharing the repository link:

1. Add the actual `TwoConnectedTanks` executable and all dependent runtime
   files to `model_runtime/`.
2. Verify the application can launch that executable from the GUI.
3. Push the repository to GitHub.
4. Share the GitHub repository link as required.

## References

- OpenModelica simulation runtime flags:
  https://openmodelica.org/doc/OpenModelicaUsersGuide/latest/simulationflags.html
- OpenModelica `buildModel` scripting reference:
  https://build.openmodelica.org/Documentation/OpenModelica.Scripting.buildModel.html
- OpenModelica Linux downloads:
  https://openmodelica.org/download/download-linux
- OpenModelica Windows downloads:
  https://openmodelica.org/download/download-windows/

## Suggested Improvements

If you want to polish this further before submission, the next useful additions
would be:

- screenshots or a short demo GIF in the repository
- a packaged executable of the Python GUI using `pyinstaller`
- logging to a file for easier debugging
