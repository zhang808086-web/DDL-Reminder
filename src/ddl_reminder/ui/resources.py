from __future__ import annotations

import sys
from pathlib import Path


def app_icon_path() -> Path:
    bundled_root = getattr(sys, "_MEIPASS", None)
    if bundled_root is not None:
        return Path(bundled_root) / "ddl_reminder" / "ui" / "assets" / "app_icon.ico"

    return Path(__file__).resolve().parent / "assets" / "app_icon.ico"
