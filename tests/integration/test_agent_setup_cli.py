import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


@pytest.mark.parametrize("entry", ["source", "packaged"])
def test_setup_command_detects_later_clients_and_is_repeatable(tmp_path, entry):
    executable = os.environ.get("DDL_MCP_EXECUTABLE")
    if entry == "packaged" and not executable:
        pytest.skip("Set DDL_MCP_EXECUTABLE to verify the packaged setup command")
    if entry == "source":
        # Source execution intentionally targets an installed binary; use a
        # fixture at its standard local-appdata location, never the real one.
        installed = tmp_path / "local/Programs/DDL Reminder/DDL-Reminder-MCP.exe"
        installed.parent.mkdir(parents=True)
        installed.touch()
    env = dict(os.environ,
               PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src"),
               APPDATA=str(tmp_path / "data"), LOCALAPPDATA=str(tmp_path / "local"),
               USERPROFILE=str(tmp_path),
               CLAUDE_CONFIG_DIR=str(tmp_path / ".claude"),
               CODEX_HOME=str(tmp_path / ".codex"), DSH_HOME=str(tmp_path / ".dsh"))
    command = [executable] if entry == "packaged" else [sys.executable, "-m", "ddl_reminder.mcp_server"]

    def run():
        result = subprocess.run([*command, "--connect-agents"], env=env,
                                capture_output=True, timeout=30)
        assert result.returncode == 0, result.stderr.decode(errors="replace")
        return json.loads((tmp_path / "data/DDL-Reminder/agent-setup.json").read_text(encoding="utf-8"))

    assert len(run()) == 2
    assert (tmp_path / ".claude/.claude.json").exists()
    assert (tmp_path / ".codex/config.toml").exists()
    profile = tmp_path / ".dsh/profiles/desktop"
    profile.mkdir(parents=True)
    (profile / "package.json").write_text('{}', encoding="utf-8")
    module = profile / "node_modules/@deepseek-ai/dsh-mcp-client"
    module.mkdir(parents=True)
    (module / "package.json").write_text('{}', encoding="utf-8")
    assert len(run()) == 3
    before = (profile / "cordis.patch.yml").read_bytes()
    run()
    assert (profile / "cordis.patch.yml").read_bytes() == before
