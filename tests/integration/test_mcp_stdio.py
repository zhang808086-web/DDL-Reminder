"""Exercise the real wire protocol, source entry point and optional frozen exe."""

import asyncio
import json
import os
from pathlib import Path
import sqlite3
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import pytest


def decoded(result):
    assert not result.isError, result.content
    if result.structuredContent is not None:
        return result.structuredContent.get("result", result.structuredContent)
    return json.loads(result.content[0].text)


@pytest.mark.parametrize("entry", ["source", "packaged"])
def test_mcp_round_trip_persistence_validation_and_concurrent_clients(tmp_path, entry):
    executable = os.environ.get("DDL_MCP_EXECUTABLE")
    if entry == "packaged" and not executable:
        pytest.skip("Set DDL_MCP_EXECUTABLE to verify a frozen MCP executable")
    environment = dict(os.environ, APPDATA=str(tmp_path),
                       PYTHONPATH=str(Path(__file__).resolve().parents[2] / "src"))
    parameters = StdioServerParameters(
        command=executable if entry == "packaged" else sys.executable,
        args=[] if entry == "packaged" else ["-m", "ddl_reminder.mcp_server"],
        env=environment,
    )

    async def exercise():
        async with stdio_client(parameters) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                assert {tool.name for tool in tools.tools} == {
                    "get_local_time", "create_task", "list_tasks", "get_task"
                }
                assert "local_time" in decoded(await session.call_tool("get_local_time", {}))
                created = decoded(await session.call_tool("create_task", {
                    "title": "代理创建测试", "deadline_date": "2028-02-29",
                    "description": "隔离数据库，仅用于发布验证",
                }))
                assert created["deadline"] == "2028-02-29T23:59"
                assert created["completed"] is False
                task_id = created["id"]
                assert decoded(await session.call_tool("get_task", {"task_id": task_id})) == created
                for values in [
                    {"deadline_date": "2026-02-29"},
                    {"deadline_time": "24:00"},
                    {"title": "0123456789abcdef"},
                ]:
                    arguments = {"title": "无效任务", "deadline_date": "2028-02-29", **values}
                    assert (await session.call_tool("create_task", arguments)).isError
                assert (await session.call_tool("get_task", {"task_id": 99999})).isError
                assert (await session.call_tool("list_tasks", {"limit": 0})).isError
                tasks = decoded(await session.call_tool("list_tasks", {}))
                assert [task["id"] for task in tasks] == [task_id]

        # A fresh server process must see the first process's committed task.
        async def another_client(index):
            async with stdio_client(parameters) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    assert decoded(await session.call_tool("get_task", {"task_id": task_id})) == created
                    return decoded(await session.call_tool("create_task", {
                        "title": f"并发任务{index}", "deadline_date": "2028-03-01",
                    }))["id"]

        ids = await asyncio.gather(another_client(1), another_client(2))
        assert len(set(ids)) == 2

    asyncio.run(asyncio.wait_for(exercise(), timeout=60))
    with sqlite3.connect(tmp_path / "DDL-Reminder" / "tasks.db") as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert connection.execute("SELECT COUNT(*) FROM tasks").fetchone()[0] == 3
