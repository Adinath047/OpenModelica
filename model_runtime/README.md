# OpenModelica Runtime Bundle

Copy the generated `TwoConnectedTanks` executable and every dependent file that
OpenModelica creates into this directory before submitting the repository.

Typical contents include:

- `TwoConnectedTanks` or `TwoConnectedTanks.exe`
- simulation support files generated beside the executable
- any runtime DLLs / shared libraries required on the target OS

The launcher application can then browse to the executable from this folder.

For local GUI testing before the real model is compiled, you can also use the
included `demo_two_connected_tanks.sh` script on Unix-like systems.

On Windows, use `demo_two_connected_tanks.bat`.
