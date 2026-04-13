"""PyQt6 user interface for launching OpenModelica simulation executables."""

from __future__ import annotations

import sys
from pathlib import Path

from PyQt6.QtCore import QProcess, Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSizePolicy,
    QStatusBar,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from openmodelica_launcher.core import ValidationError, build_request, format_command


class LauncherWindow(QMainWindow):
    """Main window for selecting and launching a simulation executable."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("OpenModelica Desktop Launcher")
        self.setMinimumWidth(720)
        self.process: QProcess | None = None

        self.app_input = QLineEdit()
        self.start_time_input = QLineEdit()
        self.stop_time_input = QLineEdit()
        self.command_preview = QLabel("Command preview will appear here.")
        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        self.output_box.setPlaceholderText(
            "Process output will be displayed here after execution."
        )
        self.run_button = QPushButton("Run Simulation")
        self.clear_button = QPushButton("Clear Output")
        self.status_bar = QStatusBar(self)
        self.setStatusBar(self.status_bar)

        self._build_ui()

    def _build_ui(self) -> None:
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        form_layout = QFormLayout()

        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self._select_application)

        app_layout = QHBoxLayout()
        app_layout.addWidget(self.app_input)
        app_layout.addWidget(browse_button)

        integer_validator = QIntValidator(0, 4, self)
        self.start_time_input.setPlaceholderText("0")
        self.stop_time_input.setPlaceholderText("4")
        self.start_time_input.setValidator(integer_validator)
        self.stop_time_input.setValidator(integer_validator)

        form_layout.addRow("Application", app_layout)
        form_layout.addRow("Start time", self.start_time_input)
        form_layout.addRow("Stop time", self.stop_time_input)

        button_layout = QHBoxLayout()
        self.run_button.clicked.connect(self._launch_simulation)
        self.clear_button.clicked.connect(self.output_box.clear)
        button_layout.addWidget(self.run_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()

        self.command_preview.setWordWrap(True)
        self.command_preview.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum,
        )
        self.command_preview.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )

        main_layout.addLayout(form_layout)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(QLabel("Command Preview"))
        main_layout.addWidget(self.command_preview)
        main_layout.addWidget(QLabel("Execution Output"))
        main_layout.addWidget(self.output_box)

        central_widget.setLayout(main_layout)
        self.status_bar.showMessage("Select an OpenModelica executable to begin.")

    def _select_application(self) -> None:
        default_dir = Path.cwd() / "model_runtime"
        if not default_dir.exists():
            default_dir = Path.cwd()
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select OpenModelica Executable",
            str(default_dir),
        )
        if selected_path:
            self.app_input.setText(selected_path)
            self.status_bar.showMessage("Executable selected.")

    def _launch_simulation(self) -> None:
        try:
            request = build_request(
                executable_path=self.app_input.text(),
                start_time_text=self.start_time_input.text(),
                stop_time_text=self.stop_time_input.text(),
            )
        except ValidationError as error:
            self.command_preview.setText("Validation failed.")
            self.output_box.clear()
            self.status_bar.showMessage("Validation failed.")
            QMessageBox.warning(self, "Invalid Input", str(error))
            return

        command = request.command()
        self.command_preview.setText(format_command(command))
        self.output_box.clear()

        self.process = QProcess(self)
        self.process.setProgram(command[0])
        self.process.setArguments(command[1:])
        self.process.readyReadStandardOutput.connect(self._append_stdout)
        self.process.readyReadStandardError.connect(self._append_stderr)
        self.process.finished.connect(self._handle_finished)
        self.process.errorOccurred.connect(self._handle_process_error)

        self.run_button.setEnabled(False)
        self.status_bar.showMessage("Simulation running...")
        self.output_box.append("Launching executable...\n")
        self.process.start()

    def _append_stdout(self) -> None:
        if self.process is None:
            return
        data = bytes(self.process.readAllStandardOutput()).decode(
            "utf-8",
            errors="replace",
        )
        if data:
            self.output_box.append(data.rstrip())

    def _append_stderr(self) -> None:
        if self.process is None:
            return
        data = bytes(self.process.readAllStandardError()).decode(
            "utf-8",
            errors="replace",
        )
        if data:
            self.output_box.append(f"[stderr]\n{data.rstrip()}")

    def _handle_finished(self, exit_code: int, _exit_status: QProcess.ExitStatus) -> None:
        self.run_button.setEnabled(True)
        self.status_bar.showMessage(f"Simulation finished with exit code {exit_code}.")
        if exit_code == 0:
            QMessageBox.information(
                self,
                "Simulation Complete",
                "The simulation executable finished successfully.",
            )
        else:
            QMessageBox.warning(
                self,
                "Simulation Finished With Errors",
                f"The executable returned exit code {exit_code}.",
            )

    def _handle_process_error(self, error: QProcess.ProcessError) -> None:
        self.run_button.setEnabled(True)
        self.status_bar.showMessage("Simulation launch failed.")
        QMessageBox.critical(
            self,
            "Launch Failed",
            f"The application could not be started.\nQt process error: {error.name}",
        )


def main() -> int:
    app = QApplication(sys.argv)
    window = LauncherWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
