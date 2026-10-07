from __future__ import annotations

import sys
from pathlib import Path


def _qml_root() -> Path:
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root is not None:
        return Path(frozen_root) / "ddl_reminder" / "ui" / "qml"
    return Path(__file__).resolve().parent / "qml"


def qml_path(name: str) -> Path:
    root = _qml_root().resolve()
    candidate = (root / name).resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError("QML resource must stay inside the QML directory")
    return candidate
