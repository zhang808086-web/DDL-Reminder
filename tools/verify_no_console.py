"""Passive Windows window-event audit for the background registration binary.

No windows are clicked or manipulated. Launch the binary without hide flags so
the check cannot pass solely because its caller hid an allocated console.
"""

import argparse
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import time


def subsystem(path):
    data = Path(path).read_bytes()
    pe = struct.unpack_from("<I", data, 0x3C)[0]
    assert data[pe:pe + 4] == b"PE\0\0"
    return struct.unpack_from("<H", data, pe + 4 + 20 + 68)[0]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("executable")
    parser.add_argument("--repeat", type=int, default=5)
    parser.add_argument("--task-name")
    parser.add_argument("--observe-seconds", type=float, default=0)
    args = parser.parse_args()
    assert os.name == "nt"
    executable = str(Path(args.executable).resolve())
    assert subsystem(executable) == 2, "Background executable must use IMAGE_SUBSYSTEM_WINDOWS_GUI"
    user = ctypes.WinDLL("user32", use_last_error=True)
    callback_type = ctypes.WINFUNCTYPE(None, wintypes.HANDLE, wintypes.DWORD, wintypes.HWND,
                                     wintypes.LONG, wintypes.LONG, wintypes.DWORD, wintypes.DWORD)
    user.SetWinEventHook.argtypes = [wintypes.DWORD, wintypes.DWORD, wintypes.HMODULE,
                                    callback_type, wintypes.DWORD, wintypes.DWORD, wintypes.DWORD]
    user.SetWinEventHook.restype = wintypes.HANDLE
    user.UnhookWinEvent.argtypes = [wintypes.HANDLE]
    user.GetClassNameW.argtypes = [wintypes.HWND, wintypes.LPWSTR, ctypes.c_int]
    user.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
    user.IsWindowVisible.argtypes = [wintypes.HWND]
    user.GetAncestor.argtypes = [wintypes.HWND, wintypes.UINT]
    user.GetAncestor.restype = wintypes.HWND
    user.PeekMessageW.argtypes = [ctypes.POINTER(wintypes.MSG), wintypes.HWND,
                                 wintypes.UINT, wintypes.UINT, wintypes.UINT]
    target_pids, windows, consoles = set(), [], []

    @callback_type
    def on_event(_hook, event, hwnd, object_id, child, _thread, _tick):
        if not hwnd or object_id != 0 or child != 0 or user.GetAncestor(hwnd, 2) != hwnd:
            return
        name = ctypes.create_unicode_buffer(256)
        user.GetClassNameW(hwnd, name, len(name))
        pid = wintypes.DWORD()
        user.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        record = {"class": name.value, "pid": pid.value, "event": event}
        if name.value in {"ConsoleWindowClass", "CASCADIA_HOSTING_WINDOW_CLASS"}:
            consoles.append(record)
        if pid.value in target_pids and user.IsWindowVisible(hwnd):
            windows.append(record)

    hook = user.SetWinEventHook(0x8000, 0x8002, None, on_event, 0, 0, 0)
    assert hook, ctypes.get_last_error()

    def pump(seconds):
        deadline = time.monotonic() + seconds
        message = wintypes.MSG()
        while time.monotonic() < deadline:
            while user.PeekMessageW(ctypes.byref(message), None, 0, 0, 1):
                user.TranslateMessage(ctypes.byref(message))
                user.DispatchMessageW(ctypes.byref(message))
            time.sleep(0.01)

    task_times = set()
    try:
        with tempfile.TemporaryDirectory(prefix="ddl-window-audit-") as directory:
            root = Path(directory)
            env = dict(os.environ, USERPROFILE=directory, APPDATA=str(root / "data"),
                       CLAUDE_CONFIG_DIR=str(root / ".claude"),
                       CODEX_HOME=str(root / ".codex"), DSH_HOME=str(root / ".dsh"))
            for _ in range(args.repeat):
                process = subprocess.Popen([executable], env=env)
                target_pids.add(process.pid)
                deadline = time.monotonic() + 20
                while process.poll() is None and time.monotonic() < deadline:
                    pump(0.05)
                if process.poll() is None:
                    process.kill()
                    raise AssertionError("Background registration timed out")
                assert process.returncode == 0, process.returncode
                report = json.loads((root / "data/DDL-Reminder/agent-setup.json").read_text(encoding="utf-8"))
                assert len(report) == 2 and all(item["success"] for item in report)
                pump(0.2)
        if args.task_name:
            import win32com.client
            service = win32com.client.Dispatch("Schedule.Service")
            service.Connect()
            folder = service.GetFolder("\\")
            task = folder.GetTask(args.task_name)
            assert Path(task.Definition.Actions.Item(1).Path) == Path(executable)
            assert not task.Definition.Actions.Item(1).Arguments
            task.Run(None)
            deadline = time.monotonic() + args.observe_seconds
            while time.monotonic() < deadline:
                pump(0.5)
                task = folder.GetTask(args.task_name)
                task_times.add(str(task.LastRunTime))
            assert task.LastTaskResult == 0, task.LastTaskResult
            assert len(task_times) >= 2, "Did not observe both manual and periodic task execution"
        assert not windows, windows
        assert not consoles, consoles
        print(json.dumps({"gui_subsystem": 2, "ordinary_launches": args.repeat,
                          "visible_background_windows": windows, "console_events": consoles,
                          "scheduled_run_timestamps": sorted(task_times),
                          "observed_seconds": args.observe_seconds}), flush=True)
    finally:
        user.UnhookWinEvent(hook)


if __name__ == "__main__":
    main()
