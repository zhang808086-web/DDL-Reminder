from pathlib import Path

import ddl_reminder.infrastructure.autostart as autostart_module
from ddl_reminder.infrastructure.autostart import (
    AUTOSTART_ARG,
    WindowsAutostart,
    build_autostart_command,
    is_autostart_launch,
)


def test_build_autostart_command_quotes_executable_path():
    command = build_autostart_command(
        Path(r"C:\Program Files\DDL-Reminder\DDL-Reminder.exe")
    )

    assert command == rf'"C:\Program Files\DDL-Reminder\DDL-Reminder.exe" {AUTOSTART_ARG}'


def test_is_autostart_launch_detects_autostart_argument():
    assert is_autostart_launch(["DDL-Reminder.exe", AUTOSTART_ARG])


def test_is_autostart_launch_is_false_without_autostart_argument():
    assert not is_autostart_launch(["DDL-Reminder.exe"])


class FakeRegistryKey:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class FakeWinreg:
    HKEY_CURRENT_USER = object()
    KEY_READ = 1
    KEY_SET_VALUE = 2
    REG_SZ = 1

    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    def OpenKey(self, *args):
        return FakeRegistryKey()

    def SetValueEx(self, key, name, reserved, value_type, value) -> None:
        self.values[name] = value

    def DeleteValue(self, key, name) -> None:
        if name not in self.values:
            raise FileNotFoundError

        del self.values[name]

    def QueryValueEx(self, key, name):
        if name not in self.values:
            raise FileNotFoundError

        return self.values[name], self.REG_SZ


def test_windows_autostart_enable_writes_command(monkeypatch):
    fake_winreg = FakeWinreg()
    monkeypatch.setattr(autostart_module, "winreg", fake_winreg)

    autostart = WindowsAutostart()
    autostart.enable('"DDL-Reminder.exe" --autostart')

    assert fake_winreg.values["DDL-Reminder"] == '"DDL-Reminder.exe" --autostart'


def test_windows_autostart_disable_deletes_command(monkeypatch):
    fake_winreg = FakeWinreg()
    fake_winreg.values["DDL-Reminder"] = '"DDL-Reminder.exe" --autostart'
    monkeypatch.setattr(autostart_module, "winreg", fake_winreg)

    WindowsAutostart().disable()

    assert "DDL-Reminder" not in fake_winreg.values


def test_windows_autostart_disable_ignores_missing_value(monkeypatch):
    fake_winreg = FakeWinreg()
    monkeypatch.setattr(autostart_module, "winreg", fake_winreg)

    WindowsAutostart().disable()

    assert fake_winreg.values == {}


def test_windows_autostart_is_enabled_requires_expected_command_when_given(monkeypatch):
    fake_winreg = FakeWinreg()
    fake_winreg.values["DDL-Reminder"] = '"C:\\Old\\DDL-Reminder.exe" --autostart'
    monkeypatch.setattr(autostart_module, "winreg", fake_winreg)

    autostart = WindowsAutostart()

    assert autostart.is_enabled()
    assert not autostart.is_enabled('"C:\\New\\DDL-Reminder.exe" --autostart')
    assert autostart.is_enabled('"C:\\Old\\DDL-Reminder.exe" --autostart')
