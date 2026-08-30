from __future__ import annotations

from dataclasses import dataclass
import os
import subprocess
from typing import Protocol


@dataclass(slots=True, frozen=True)
class InsertionResult:
    ok: bool
    returncode: int
    method: str


class InjectionBroker(Protocol):
    """Only boundary allowed to synthesize global user input."""

    def insert(self, text: str, *, trailing_space: bool = True) -> InsertionResult: ...
    def press_enter(self) -> InsertionResult: ...


class YdotoolInjector:
    def __init__(self, socket_path: str, key_delay: str = "1", key_hold: str = "1") -> None:
        self.socket_path = socket_path
        self.key_delay = key_delay
        self.key_hold = key_hold

    def _env(self) -> dict[str, str]:
        return dict(os.environ, YDOTOOL_SOCKET=self.socket_path)

    def insert(self, text: str, *, trailing_space: bool = True) -> InsertionResult:
        if not text:
            return InsertionResult(True, 0, "ydotool")
        payload = text + (" " if trailing_space else "")
        result = subprocess.run(
            ["ydotool", "type", "-d", self.key_delay, "-H", self.key_hold, "-f", "-"],
            input=payload.encode("utf-8"),
            env=self._env(),
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        return InsertionResult(result.returncode == 0, result.returncode, "ydotool")

    def press_enter(self) -> InsertionResult:
        result = subprocess.run(
            ["ydotool", "key", "28:1", "28:0"],
            env=self._env(),
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        return InsertionResult(result.returncode == 0, result.returncode, "ydotool")
