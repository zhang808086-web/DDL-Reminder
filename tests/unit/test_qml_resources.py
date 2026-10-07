from pathlib import Path

from ddl_reminder.ui.qml_resources import qml_path


def test_qml_path_resolves_source_tree_files():
    main_qml = qml_path("Main.qml")

    assert main_qml.is_file()
    assert main_qml.name == "Main.qml"
    assert main_qml.parent.name == "qml"


def test_qml_path_resolves_frozen_bundle(monkeypatch, tmp_path):
    bundled = tmp_path / "ddl_reminder" / "ui" / "qml"
    bundled.mkdir(parents=True)
    expected = bundled / "Main.qml"
    expected.write_text("// bundled", encoding="utf-8")
    monkeypatch.setattr("sys._MEIPASS", str(tmp_path), raising=False)

    assert qml_path("Main.qml") == expected


def test_qml_path_rejects_parent_traversal():
    try:
        qml_path("../main.py")
    except ValueError as error:
        assert "QML directory" in str(error)
    else:
        raise AssertionError("parent traversal must be rejected")
