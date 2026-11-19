# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path

from PyInstaller.utils.hooks import collect_submodules

block_cipher = None


a = Analysis(
    ["src\\ddl_reminder\\main.py"],
    pathex=["src"],
    binaries=[],
    datas=[
        ("src\\ddl_reminder\\ui\\assets\\app_icon.ico", "ddl_reminder\\ui\\assets"),
        ("src\\ddl_reminder\\ui\\qml", "ddl_reminder\\ui\\qml"),
    ],
    hiddenimports=[
        "PySide6.QtQml",
        "PySide6.QtQuick",
        "PySide6.QtQuickControls2",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets",
        "PySide6.QtWebEngineQuick", "PySide6.Qt3DCore", "PySide6.Qt3DRender",
        "PySide6.Qt3DInput", "PySide6.Qt3DLogic", "PySide6.Qt3DAnimation",
        "PySide6.Qt3DExtras", "PySide6.QtCharts", "PySide6.QtGraphs",
        "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets",
        "PySide6.QtPositioning", "PySide6.QtLocation", "PySide6.QtSensors",
        "PySide6.QtSerialPort", "PySide6.QtBluetooth", "PySide6.QtNfc",
        "PySide6.QtPdf", "PySide6.QtPdfWidgets", "PySide6.QtSql",
        "PySide6.QtTest", "PySide6.QtDesigner", "PySide6.QtHelp",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

def _should_bundle_binary(entry) -> bool:
    binary_name = os.path.basename(entry[0]).lower()
    destination_dir = os.path.dirname(entry[0]).replace("\\", "/").lower()
    if destination_dir not in ("", "."):
        return True

    return not (
        binary_name == "ucrtbase.dll"
        or binary_name.startswith("api-ms-win-")
        or binary_name.startswith("vcruntime")
        or binary_name.startswith("msvcp")
        or binary_name.startswith("icu")
    )


# Let Windows use its installed runtime, API-set shims, and ICU libraries.
# Bundling environment copies at the bundle root can shadow compatible DLLs and
# prevent Qt6 from loading with an entry-point error on the target machine.
a.binaries = [
    entry
    for entry in a.binaries
    if _should_bundle_binary(entry)
]

# QML's hook may collect every installed module. Retain the QtQuick/QtQml
# families used by this UI, including their implementation and style plugins.
# Keep the software renderer for machines without a compatible GPU driver.
def _used_qt_resource(entry):
    destination = entry[0].replace("\\", "/")
    if destination.startswith("PySide6/translations/"):
        return False
    if destination.startswith("PySide6/qml/"):
        if destination.startswith((
            "PySide6/qml/QtQuick/Pdf/", "PySide6/qml/QtQuick/Scene2D/",
            "PySide6/qml/QtQuick/Scene3D/",
        )):
            return False
        module = destination[len("PySide6/qml/"):].split("/")[0]
        return module in {"QtQuick", "QtQml"}
    name = Path(destination).name.lower()
    if name == "qpdf.dll" and "/plugins/imageformats/" in destination:
        return False
    return not name.startswith((
        "qt6webengine", "qt63d", "qt6quick3d", "qt6charts", "qt6graphs",
        "qt6multimedia", "qt6positioning", "qt6location", "qt6sensors",
        "qt6serialport", "qt6bluetooth", "qt6nfc", "qt6pdf",
    ))


a.binaries = [entry for entry in a.binaries if _used_qt_resource(entry)]
a.datas = [entry for entry in a.datas if _used_qt_resource(entry)]

# A console-subsystem executable is required for MCP stdin/stdout. Both
# executables share one _internal directory, so common dependencies ship once.
mcp_analysis = Analysis(
    ["src\\ddl_reminder\\mcp_server.py"],
    pathex=["src"],
    hiddenimports=collect_submodules("mcp.server.fastmcp"),
    excludes=["PySide6", "tkinter", "pytest"],
)
mcp_analysis.binaries = [
    entry for entry in mcp_analysis.binaries if _should_bundle_binary(entry)
]
mcp_pyz = PYZ(mcp_analysis.pure)
mcp_exe = EXE(
    mcp_pyz,
    mcp_analysis.scripts,
    [],
    exclude_binaries=True,
    name="DDL-Reminder-MCP",
    console=True,
    icon="src\\ddl_reminder\\ui\\assets\\app_icon.ico",
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="DDL-Reminder",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="src\\ddl_reminder\\ui\\assets\\app_icon.ico",
)
coll = COLLECT(
    exe,
    mcp_exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    mcp_analysis.binaries,
    mcp_analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DDL-Reminder",
)
