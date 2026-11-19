"""Read-only local client smoke check; uses the user's configured model account."""

import argparse
import json
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("client", choices=["claude", "codex"])
parser.add_argument("command")
parser.add_argument("--model")
args = parser.parse_args()
prompt = (
    "这是 MCP 接入验证。只调用 ddl-reminder MCP 服务的 get_local_time 工具一次，"
    "随后仅回复该工具返回的 local_time。不要创建、读取或修改任务，不要使用其他工具。"
)
if args.client == "claude":
    command = [args.command, "-p", "--output-format", "json", "--max-turns", "3",
               "--allowedTools", "mcp__ddl-reminder__get_local_time", "--", prompt]
    if args.model:
        command[1:1] = ["--model", args.model]
    if args.command.endswith(".ps1"):
        command = ["powershell.exe", "-NoProfile", "-File", *command]
else:
    command = [args.command, "exec", "--json", "--ephemeral", "--skip-git-repo-check",
               "--sandbox", "read-only", "-c", 'mcp_servers.ddl-reminder.tools.get_local_time.approval_mode="approve"', prompt]
result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180)
events = []
for line in result.stdout.splitlines():
    try:
        event = json.loads(line)
    except ValueError:
        continue
    if args.client == "claude":
        events.append({key: event[key] for key in ("type", "subtype", "is_error", "result") if key in event})
    else:
        item = event.get("item", {})
        if item.get("type") in {"mcp_tool_call", "agent_message"}:
            events.append({"type": item.get("type"), "server": item.get("server"),
                           "tool": item.get("tool"), "status": item.get("status"),
                           "text": item.get("text"), "result": item.get("result")})
        elif event.get("type") in {"error", "turn.failed"}:
            events.append(event)
print(json.dumps({"client": args.client, "exit": result.returncode, "events": events}, ensure_ascii=True))
if result.returncode:
    print(result.stderr[-1200:])
raise SystemExit(result.returncode)
