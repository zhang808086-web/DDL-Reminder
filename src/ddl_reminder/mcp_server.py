"""Per-user MCP stdio entry point; deliberately independent of Qt."""

import logging
import sys
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from ddl_reminder.application.task_service import TaskService
from ddl_reminder.domain.deadline_input import parse_deadline
from ddl_reminder.domain.task import Task
from ddl_reminder.infrastructure.app_paths import get_database_path
from ddl_reminder.infrastructure.database import (
    create_session_factory,
    create_sqlite_engine,
    init_database,
)
from ddl_reminder.infrastructure.sqlalchemy_task_repository import SQLAlchemyTaskRepository


def task_data(task: Task) -> dict:
    return {
        "id": task.id,
        "title": task.title,
        "description": task.description or "",
        "deadline": task.deadline.isoformat(timespec="minutes"),
        "completed": task.is_completed,
        "created_at": task.created_at.isoformat(),
    }


def create_server(service: TaskService) -> FastMCP:
    server = FastMCP(
        "DDL Reminder",
        instructions=(
            "Manage this Windows user's local DDL Reminder tasks. "
            "Use get_local_time before resolving relative dates. Deadlines use "
            "the user's local wall clock without a timezone suffix. Never invent "
            "a deadline; ask the user if it is ambiguous. Titles have at most 15 characters."
        ),
    )

    @server.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False))
    def get_local_time() -> dict:
        """Get the computer's current local time and UTC offset for relative dates."""
        return {"local_time": datetime.now().astimezone().isoformat()}

    @server.tool(annotations=ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False))
    def create_task(
        title: str, deadline_date: str, deadline_time: str = "23:59", description: str = ""
    ) -> dict:
        """Create one task. Date: YYYY-MM-DD; time: HH:MM (00:00–23:59).

        Dates in the past are allowed and will appear as overdue. Call only when
        the user requested creation. Avoid repeating a successful call.
        """
        day, clock = parse_deadline(deadline_date, deadline_time)
        task = service.create_task(title, day, clock, description)
        return task_data(task)

    @server.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False))
    def list_tasks(completed: bool = False, limit: int = 50) -> list[dict]:
        """List active tasks by default, sorted by deadline; limit is 1–200."""
        if not 1 <= limit <= 200:
            raise ValueError("limit 必须在 1–200 之间")
        tasks = service.list_completed_tasks() if completed else service.list_active_tasks()
        return [task_data(task) for task in sorted(
            tasks, key=lambda task: (task.deadline, task.created_at)
        )[:limit]]

    @server.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False))
    def get_task(task_id: int) -> dict:
        """Read a task by its ID, including its deadline and completion state."""
        return task_data(service.get_task(task_id))

    return server


def main() -> int:
    if sys.argv[1:] == ["--connect-agents"]:
        import json
        from ddl_reminder.infrastructure.agent_setup import connect_agents, installed_mcp_command
        from ddl_reminder.infrastructure.app_paths import get_app_data_dir
        results = connect_agents(installed_mcp_command())
        report = json.dumps(results, ensure_ascii=False, indent=2)
        (get_app_data_dir() / "agent-setup.json").write_text(report, encoding="utf-8")
        print(report)
        return 0 if all(item["success"] for item in results) else 1
    # stdout is reserved for the MCP protocol, including in the packaged executable.
    logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
    path = get_database_path()
    engine = create_sqlite_engine(f"sqlite:///{path.as_posix()}")
    try:
        init_database(engine)
        repository = SQLAlchemyTaskRepository(create_session_factory(engine))
        create_server(TaskService(repository)).run(transport="stdio")
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
