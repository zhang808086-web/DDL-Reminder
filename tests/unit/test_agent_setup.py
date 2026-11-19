import json
from pathlib import Path
import tomllib

import pytest
import yaml

from ddl_reminder.infrastructure.agent_setup import (
    configure_claude, configure_codex, configure_deepseek, connect_agents,
)

COMMAND = r"C:\Users\用户\AppData\Local\Programs\DDL Reminder\DDL-Reminder-MCP.exe"


@pytest.fixture(autouse=True)
def available_dsh_client(monkeypatch):
    monkeypatch.setattr("ddl_reminder.infrastructure.agent_setup._deepseek_client",
                        lambda _path: "@deepseek-ai/dsh-mcp-client")


def test_claude_preserves_other_settings_and_makes_backup(tmp_path):
    path = tmp_path / ".claude.json"
    before = {"preferences": {"x": True}, "mcpServers": {"other": {"command": "other.exe"}}}
    path.write_text(json.dumps(before), encoding="utf-8")
    original = path.read_bytes()
    configure_claude(path, COMMAND)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["preferences"] == before["preferences"]
    assert data["mcpServers"]["other"] == before["mcpServers"]["other"]
    assert data["mcpServers"]["ddl-reminder"]["command"] == COMMAND
    assert next(tmp_path.glob("*.ddl-backup-*")).read_bytes() == original
    after = path.read_bytes()
    assert configure_claude(path, COMMAND) == "已接入"
    assert path.read_bytes() == after


def test_codex_preserves_comments_tables_and_is_idempotent(tmp_path):
    path = tmp_path / "config.toml"
    original = '# keep\nmodel = "example"\n[mcp_servers.other]\ncommand="other"\n'
    path.write_text(original, encoding="utf-8")
    configure_codex(path, COMMAND)
    text = path.read_text(encoding="utf-8")
    assert text.startswith(original)
    assert tomllib.loads(text)["mcp_servers"]["ddl-reminder"]["command"] == COMMAND
    configure_codex(path, COMMAND)
    assert path.read_text(encoding="utf-8") == text
    assert len(list(tmp_path.glob("*.ddl-backup-*"))) == 1


@pytest.mark.parametrize("original", [
    '# comment\n- id: other\n  config:\n    value: !!js process.env.SECRET\n',
    '# empty\n[]\n',
    '',
])
def test_dsh_preserves_js_tags_and_only_inserts_one_entry(tmp_path, original):
    path = tmp_path / "cordis.patch.yml"
    path.write_text(original, encoding="utf-8")
    configure_deepseek(path, COMMAND)
    after = path.read_text(encoding="utf-8")
    yaml.compose(after, Loader=yaml.BaseLoader)
    assert '- insert:' in after
    assert after.count("serverName: ddl-reminder") == 1
    if "!!js" in original:
        assert original in after
    configure_deepseek(path, COMMAND)
    assert path.read_text(encoding="utf-8") == after


@pytest.mark.parametrize("configure,text", [
    (configure_claude, '{"mcpServers":{"ddl-reminder":{"command":"other"}}}'),
    (configure_codex, '[mcp_servers.ddl-reminder]\ncommand="other"\n'),
    (configure_deepseek, '- id: mcp-ddl-reminder\n  config:\n    command: other\n'),
    (configure_claude, '{ broken'), (configure_codex, '[broken'),
    (configure_deepseek, 'unexpected: mapping'),
])
def test_conflicts_and_invalid_documents_are_not_overwritten(tmp_path, configure, text):
    path = tmp_path / "config"
    path.write_text(text, encoding="utf-8")
    original = path.read_bytes()
    with pytest.raises((ValueError, yaml.YAMLError)):
        configure(path, COMMAND)
    assert path.read_bytes() == original
    assert list(tmp_path.glob("*.ddl-backup-*")) == []


def test_clients_installed_later_are_preset_or_discovered(tmp_path, monkeypatch):
    for key in ("CLAUDE_CONFIG_DIR", "CODEX_HOME", "DSH_HOME"):
        monkeypatch.delenv(key, raising=False)
    executable = tmp_path / "DDL-Reminder-MCP.exe"
    executable.touch()
    first = connect_agents(str(executable), tmp_path)
    assert all(row["success"] for row in first)
    assert (tmp_path / ".claude.json").is_file()
    assert (tmp_path / ".codex/config.toml").is_file()
    profile = tmp_path / ".dsh/profiles/desktop"
    profile.mkdir(parents=True)
    (profile / "package.json").write_text('{}', encoding="utf-8")
    later = connect_agents(str(executable), tmp_path)
    assert len(later) == 3 and all(row["success"] for row in later)
    assert "ddl-reminder" in (profile / "cordis.patch.yml").read_text(encoding="utf-8")


def test_automatic_reconnect_preserves_user_disabled_codex_server(tmp_path):
    path = tmp_path / "config.toml"
    configure_codex(path, COMMAND)
    text = path.read_text(encoding="utf-8").replace('args = []', 'args = []\nenabled = false')
    path.write_text(text, encoding="utf-8")
    configure_codex(path, COMMAND)
    assert path.read_text(encoding="utf-8") == text
