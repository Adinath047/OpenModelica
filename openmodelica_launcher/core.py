"""Core validation and command-building logic for the launcher."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


class ValidationError(ValueError):
    """Raised when user-supplied launch parameters are invalid."""


@dataclass(frozen=True)
class SimulationRequest:
    """Validated request for launching an OpenModelica simulation executable."""

    executable_path: Path
    start_time: int
    stop_time: int

    def command(self) -> list[str]:
        """Return the command line expected by OpenModelica-generated binaries."""
        return [
            str(self.executable_path),
            f"-override=startTime={self.start_time},stopTime={self.stop_time}",
        ]


def build_request(
    executable_path: str,
    start_time_text: str,
    stop_time_text: str,
) -> SimulationRequest:
    """Build a validated simulation request from raw UI input."""
    path = Path(executable_path).expanduser()
    if not executable_path.strip():
        raise ValidationError("Please select an application to launch.")
    if not path.exists():
        raise ValidationError("The selected application does not exist.")
    if not path.is_file():
        raise ValidationError("The selected path must be a file.")

    start_time = _parse_integer(start_time_text, "Start time")
    stop_time = _parse_integer(stop_time_text, "Stop time")

    if start_time < 0:
        raise ValidationError("Start time must be greater than or equal to 0.")
    if stop_time >= 5:
        raise ValidationError("Stop time must be less than 5.")
    if start_time >= stop_time:
        raise ValidationError("Start time must be less than stop time.")

    return SimulationRequest(
        executable_path=path,
        start_time=start_time,
        stop_time=stop_time,
    )


def _parse_integer(value: str, label: str) -> int:
    stripped = value.strip()
    if not stripped:
        raise ValidationError(f"{label} is required.")
    try:
        return int(stripped)
    except ValueError as error:
        raise ValidationError(f"{label} must be an integer.") from error


def format_command(command: Sequence[str]) -> str:
    """Return a user-friendly command preview string."""
    return " ".join(command)

