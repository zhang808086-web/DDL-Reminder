from __future__ import annotations


import sys
import winreg
from pathlib import Path

RUN_KEY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
AUTOSTART_ARG = "--autostart"


def build_autostart_command(executable: Path | str | None = None) -> str:
    executable_path = Path(executable) if executable is not None else Path(sys.executable)
    return f'"{executable_path}" {AUTOSTART_ARG}'


def is_autostart_launch(argv: list[str]) -> bool:
    return AUTOSTART_ARG in argv[1:]


def is_packaged_app() -> bool:
    return bool(getattr(sys, "frozen", False))


class WindowsAutostart:
    def __init__(self, app_name: str = "DDL-Reminder") -> None:
        self._app_name = app_name
    
    def enable(self, command: str) -> None:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE
        ) as key:
            winreg.SetValueEx(
                key,
                self._app_name,
                0,
                winreg.REG_SZ,
                command
            )
        
    def disable(self) -> None:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY_PATH,
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            try:
                winreg.DeleteValue(key, self._app_name)
            except FileNotFoundError:
                return
        
    def is_enabled(self, expected_command: str | None = None) -> bool:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            RUN_KEY_PATH,
            0,
            winreg.KEY_READ,
        ) as key:
            try:
                actual_command, _value_type = winreg.QueryValueEx(key, self._app_name)
            except FileNotFoundError:
                return False

        if expected_command is not None:
            return actual_command == expected_command

        return True
