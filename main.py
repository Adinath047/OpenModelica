"""Entry point for the OpenModelica launcher application."""

from __future__ import annotations


def main() -> int:
    """Run the GUI with a friendly error if PyQt6 is unavailable."""
    try:
        from openmodelica_launcher.gui import main as gui_main
    except ModuleNotFoundError as error:
        if error.name != "PyQt6":
            raise
        print(
            "PyQt6 is not installed. Install dependencies with "
            "`python3 -m pip install -r requirements.txt`."
        )
        return 1

    return gui_main()


if __name__ == "__main__":
    raise SystemExit(main())
