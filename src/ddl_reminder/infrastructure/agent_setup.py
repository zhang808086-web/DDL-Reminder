"""Register this user's installed MCP executable with existing local clients.

No API keys or permission policies are changed. Existing documents are validated,
backed up, and replaced atomically; an unrelated same-name server is a conflict.
"""

import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import tomllib
from uuid import uuid4

import yaml
from yaml.nodes import MappingNode, SequenceNode

SERVER = "ddl-reminder"
BEGIN = "# BEGIN DDL-REMINDER MANAGED MCP"
END = "# END DDL-REMINDER MANAGED MCP"


def _replace(path: Path, original: bytes | None, text: str) -> str:
    if path.is_symlink():
        raise ValueError("配置文件是链接，请在客户端中手动接入")
    new = text.encode("utf-8")
    if original == new:
        return "已接入"
    path.parent.mkdir(parents=True, exist_ok=True)
    current = path.read_bytes() if path.exists() else None
    if current != original:
        raise ValueError("配置已被其他程序更新，请重试")
    backup = None
    if original is not None:
        backup = path.with_name(path.name + ".ddl-backup-" + uuid4().hex)
        shutil.copy2(path, backup)
    descriptor, temporary = tempfile.mkstemp(prefix=".ddl-mcp-", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(new)
            stream.flush()
            os.fsync(stream.fileno())
        if path.exists():
            shutil.copymode(path, temporary)
        if (path.read_bytes() if path.exists() else None) != original:
            raise ValueError("配置已被其他程序更新，请重试")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return "接入成功，原配置已备份" if backup else "接入成功"


def _read(path: Path) -> tuple[bytes | None, str]:
    if path.is_symlink():
        raise ValueError("配置文件是链接，请在客户端中手动接入")
    raw = path.read_bytes() if path.exists() else None
    return raw, raw.decode("utf-8-sig") if raw is not None else ""


def _managed(text: str, block: str) -> str:
    if BEGIN not in text and END not in text:
        return text.rstrip() + "\n\n" + BEGIN + "\n" + block + END + "\n"
    if text.count(BEGIN) != 1 or text.count(END) != 1:
        raise ValueError("接入配置标记不完整，请恢复备份后重试")
    pattern = re.compile(r"(?m)^" + re.escape(BEGIN) + r"\r?\n[\s\S]*?^" + re.escape(END) + r"(?:\r?\n|$)")
    result, count = pattern.subn(lambda _: BEGIN + "\n" + block + END + "\n", text)
    if count != 1:
        raise ValueError("接入配置标记无效")
    return result


def configure_claude(path: Path, command: str) -> str:
    original, text = _read(path)
    config = json.loads(text) if text.strip() else {}
    if not isinstance(config, dict) or not isinstance(config.get("mcpServers", {}), dict):
        raise ValueError("Claude Code 配置格式不受支持")
    servers = config.setdefault("mcpServers", {})
    expected = {"type": "stdio", "command": command, "args": []}
    if SERVER in servers:
        if all(servers[SERVER].get(key) == value for key, value in expected.items()):
            return "已接入"
        raise ValueError("已存在同名 Claude MCP，请在客户端确认后重试")
    servers[SERVER] = expected
    return _replace(path, original, json.dumps(config, ensure_ascii=False, indent=2) + "\n")


def configure_codex(path: Path, command: str) -> str:
    original, text = _read(path)
    config = tomllib.loads(text)
    entry = config.get("mcp_servers", {}).get(SERVER)
    if entry is not None:
        if entry.get("command") == command and entry.get("args", []) == []:
            return "已接入"
        raise ValueError("已存在同名 Codex MCP，请在客户端确认后重试")
    block = f'[mcp_servers."{SERVER}"]\ncommand = {json.dumps(command, ensure_ascii=False)}\nargs = []\nstartup_timeout_sec = 30\n'
    updated = _managed(text, block)
    tomllib.loads(updated)
    return _replace(path, original, updated)


def _mapping(node):
    return {key.value: value for key, value in node.value} if isinstance(node, MappingNode) else {}


def _deepseek_client(path: Path) -> str:
    module = "@deepseek-ai/dsh-mcp-client"
    if (path.parent / "node_modules" / module / "package.json").is_file():
        return module
    if path.parent.name == "desktop":
        installs = [Path(os.environ.get("LOCALAPPDATA", "")) / "Programs/DeepSeek Harness"]
        if os.name == "nt":
            import winreg
            for key_path in (r"Software\Microsoft\Windows\CurrentVersion\Uninstall",
                             r"Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"):
                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as root:
                        for index in range(winreg.QueryInfoKey(root)[0]):
                            try:
                                with winreg.OpenKey(root, winreg.EnumKey(root, index)) as key:
                                    name = winreg.QueryValueEx(key, "DisplayName")[0]
                                    if str(name).startswith("DeepSeek Harness"):
                                        installs.append(Path(winreg.QueryValueEx(key, "InstallLocation")[0]))
                            except OSError:
                                continue
                except OSError:
                    pass
        for install in installs:
            archive = install / "resources/app.asar"
            if archive.is_file():
                return (archive / "dsh/node_modules" / module / "lib/index.js").resolve().as_uri()
    global_module = Path(os.environ.get("APPDATA", "")) / "npm/node_modules/@deepseek-ai/dsh/node_modules" / module / "lib/index.js"
    if global_module.is_file():
        return global_module.resolve().as_uri()
    raise ValueError("DeepSeek 的本机 MCP 客户端组件暂不可用")


def configure_deepseek(path: Path, command: str) -> str:
    original, text = _read(path)
    # Compose nodes only: !!js expressions remain literal and are never evaluated.
    root = yaml.compose(text, Loader=yaml.BaseLoader)
    if root is not None and (not isinstance(root, SequenceNode) or root.flow_style and root.value):
        raise ValueError("DeepSeek profile 不是支持的 patch 列表")
    module = _deepseek_client(path)
    if root is not None:
        entries = []
        for item in root.value:
            insert = _mapping(item).get("insert")
            if isinstance(insert, SequenceNode):
                entries.extend(insert.value)
            else:
                entries.append(item)
        for item in entries:
            fields = _mapping(item)
            config = _mapping(fields.get("config"))
            server = config.get("serverName")
            if fields.get("id") is not None and fields["id"].value == "mcp-ddl-reminder" or server is not None and server.value == SERVER:
                # Repair only our earlier managed, non-insert patch. Such a
                # patch asserts an existing row and cannot create a new plugin.
                legacy = BEGIN in text and "- insert:" not in text.split(BEGIN)[1].split(END)[0]
                if config.get("command") is not None and config["command"].value == command and not legacy:
                    return "已接入"
                if not legacy:
                    raise ValueError("DeepSeek 已存在同名 MCP，请在客户端确认后重试")
    block = ('- insert:\n'
             '    - id: mcp-ddl-reminder\n'
             f'      name: {json.dumps(module, ensure_ascii=False)}\n'
             '      config:\n'
             '        serverName: ddl-reminder\n'
             '        transport: stdio\n'
             f'        command: {json.dumps(command, ensure_ascii=False)}\n'
             '        args: []\n'
             '        startupTimeoutMs: 30000\n')
    if root is not None and root.flow_style:
        text = text[:root.start_mark.index] + text[root.end_mark.index:]
    if BEGIN not in text and root is not None and root.end_mark.index < len(text) and "..." in text[root.end_mark.index:]:
        raise ValueError("DeepSeek patch 含显式文档结束符，请在客户端接入")
    updated = _managed(text, block)
    yaml.compose(updated, Loader=yaml.BaseLoader)
    return _replace(path, original, updated)


def connect_agents(command: str, home: Path | None = None) -> list[dict]:
    home = home or Path.home()
    command = str(Path(command).resolve())
    if not Path(command).is_file():
        raise ValueError("未找到已安装的 MCP 程序")
    claude_home = Path(os.environ.get("CLAUDE_CONFIG_DIR", str(home / ".claude")))
    claude_config = claude_home / ".claude.json" if "CLAUDE_CONFIG_DIR" in os.environ else home / ".claude.json"
    codex_home = Path(os.environ.get("CODEX_HOME", str(home / ".codex")))
    dsh_home = Path(os.environ.get("DSH_HOME", str(home / ".dsh")))
    clients = []
    # These two user-level documents may be created before the clients are
    # installed. Their future first launch discovers the preconfigured server.
    clients.append(("Claude Code", claude_config, configure_claude))
    clients.append(("Codex", codex_home / "config.toml", configure_codex))
    profiles = dsh_home / "profiles"
    if profiles.is_dir():
        for profile in sorted(profiles.iterdir()):
            if profile.is_dir() and (profile / "package.json").is_file():
                clients.append((f"DeepSeek Harness ({profile.name})", profile / "cordis.patch.yml", configure_deepseek))
    results = []
    for name, path, configure in clients:
        try:
            message = configure(path, command)
            results.append({"client": name, "success": True, "message": message})
        except (OSError, ValueError, TypeError, AttributeError, yaml.YAMLError):
            # Configuration files can contain credentials; never echo file contents.
            results.append({"client": name, "success": False, "message": "配置冲突或格式不受支持，原文件未覆盖，请检查客户端配置"})
    return results


def installed_mcp_command() -> str:
    if getattr(sys, "frozen", False):
        return str(Path(sys.executable).with_name("DDL-Reminder-MCP.exe"))
    return str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "DDL Reminder" / "DDL-Reminder-MCP.exe")
