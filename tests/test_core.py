"""Tests for launcher validation and command generation."""

# ruff: noqa: E402

from __future__ import annotations

import contextlib
import io
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import main
from openmodelica_launcher.core import ValidationError, build_request, format_command


class BuildRequestTests(unittest.TestCase):
    """Exercise validation and command generation without a GUI dependency."""

    def test_build_request_creates_openmodelica_override_command(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            executable = Path(temp_dir) / "TwoConnectedTanks"
            executable.write_text("#!/bin/sh\n", encoding="utf-8")
            executable.chmod(0o755)

            request = build_request(str(executable), "0", "4")

            self.assertEqual(
                request.command(),
                [
                    str(executable),
                    "-override=startTime=0,stopTime=4",
                ],
            )

    def test_build_request_rejects_invalid_values(self) -> None:
        test_cases = [
            ("-1", "4", "Start time must be greater than or equal to 0."),
            ("2", "2", "Start time must be less than stop time."),
            ("2", "5", "Stop time must be less than 5."),
            ("abc", "4", "Start time must be an integer."),
            ("1", "", "Stop time is required."),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            executable = Path(temp_dir) / "TwoConnectedTanks"
            executable.write_text("#!/bin/sh\n", encoding="utf-8")
            executable.chmod(0o755)

            for start_time, stop_time, message in test_cases:
                with self.subTest(start_time=start_time, stop_time=stop_time):
                    with self.assertRaisesRegex(ValidationError, message):
                        build_request(str(executable), start_time, stop_time)

    def test_build_request_requires_existing_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            missing_path = Path(temp_dir) / "missing.exe"
            with self.assertRaisesRegex(ValidationError, "does not exist"):
                build_request(str(missing_path), "0", "4")

    @unittest.skipIf(
        os.name == "nt",
        "POSIX execute bit check does not apply on Windows.",
    )
    def test_build_request_requires_executable_permissions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            executable = Path(temp_dir) / "TwoConnectedTanks"
            executable.write_text("#!/bin/sh\n", encoding="utf-8")
            executable.chmod(0o644)

            with self.assertRaisesRegex(ValidationError, "not executable"):
                build_request(str(executable), "0", "4")

    def test_format_command_returns_readable_preview(self) -> None:
        command = ["Two Connected Tanks", "-override=startTime=0,stopTime=4"]
        self.assertEqual(
            format_command(command),
            "'Two Connected Tanks' -override=startTime=0,stopTime=4",
        )


class MainEntrypointTests(unittest.TestCase):
    """Verify the CLI entry point handles missing GUI dependencies cleanly."""

    def test_main_reports_missing_pyqt6_dependency(self) -> None:
        stdout = io.StringIO()

        original_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "openmodelica_launcher.gui":
                raise ModuleNotFoundError("No module named 'PyQt6'", name="PyQt6")
            return original_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=fake_import):
            with contextlib.redirect_stdout(stdout):
                exit_code = main.main()

        self.assertEqual(exit_code, 1)
        self.assertIn("PyQt6 is not installed.", stdout.getvalue())

    def test_main_delegates_to_gui_main_when_dependency_exists(self) -> None:
        fake_gui_module = SimpleNamespace(main=lambda: 0)
        original_import = __import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "openmodelica_launcher.gui":
                return fake_gui_module
            return original_import(name, globals, locals, fromlist, level)

        with patch("builtins.__import__", side_effect=fake_import):
            exit_code = main.main()

        self.assertEqual(exit_code, 0)


if __name__ == "__main__":
    unittest.main()
