import json

from ddl_reminder import agent_background


def test_background_writes_report_without_using_stdio_or_shells(tmp_path, monkeypatch, capsys):
    from ddl_reminder.infrastructure import agent_setup, app_paths
    monkeypatch.setattr(app_paths, "get_app_data_dir", lambda: tmp_path)
    monkeypatch.setattr(agent_setup, "installed_mcp_command", lambda: "installed-mcp.exe")
    results = [{"client": "Codex", "success": True, "message": "已接入"}]
    monkeypatch.setattr(agent_setup, "connect_agents", lambda command: results)
    assert agent_background.main() == 0
    assert json.loads((tmp_path / "agent-setup.json").read_text(encoding="utf-8")) == results
    assert capsys.readouterr().out == ""


def test_background_failure_is_reported_as_exit_status_not_a_popup(tmp_path, monkeypatch, capsys):
    from ddl_reminder.infrastructure import agent_setup, app_paths
    monkeypatch.setattr(app_paths, "get_app_data_dir", lambda: tmp_path)
    monkeypatch.setattr(agent_setup, "connect_agents", lambda _command: [{"success": False}])
    assert agent_background.main() == 1
    assert capsys.readouterr().out == ""
