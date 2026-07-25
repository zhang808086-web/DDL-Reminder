from pathlib import Path

import ddl_reminder.ui.resources as resources


def test_app_icon_path_points_to_project_asset():
    assert resources.app_icon_path().name == "app_icon.ico"
    assert resources.app_icon_path().exists()


def test_app_icon_path_uses_pyinstaller_bundle_root(monkeypatch, tmp_path):
    bundled_icon = tmp_path / "ddl_reminder" / "ui" / "assets" / "app_icon.ico"
    bundled_icon.parent.mkdir(parents=True)
    bundled_icon.write_bytes(b"icon")
    monkeypatch.setattr(resources.sys, "_MEIPASS", str(tmp_path), raising=False)

    assert resources.app_icon_path() == bundled_icon
