# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None


a = Analysis(
    ["src\\ddl_reminder\\main.py"],
    pathex=["src"],
    binaries=[],
    datas=[
        ("src\\ddl_reminder\\ui\\assets", "ddl_reminder\\ui\\assets"),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="DDL-Reminder",
)
