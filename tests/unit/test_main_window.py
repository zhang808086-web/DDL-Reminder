from datetime import datetime
from types import SimpleNamespace

from ddl_reminder.domain.task import Task
from ddl_reminder.ui.main_window import MainWindow


class FakeSearchInput:
    def text(self) -> str:
        return ""


class FakeTaskService:
    def __init__(self, tasks: list[Task]) -> None:
        self.tasks = tasks

    def list_active_tasks(self) -> list[Task]:
        return self.tasks


def test_main_window_orders_tasks_by_earliest_deadline():
    later = Task(
        id=1,
        title="Later task",
        deadline=datetime(2026, 7, 23, 12, 0),
        created_at=datetime(2026, 7, 21, 9, 0),
    )
    earlier = Task(
        id=2,
        title="Earlier task",
        deadline=datetime(2026, 7, 22, 12, 0),
        created_at=datetime(2026, 7, 21, 10, 0),
    )
    window = SimpleNamespace(
        current_filter="active",
        task_service=FakeTaskService([later, earlier]),
        search_input=FakeSearchInput(),
    )

    tasks = MainWindow._tasks_for_current_filter(
        window,
        datetime(2026, 7, 21, 11, 0),
    )

    assert tasks == [earlier, later]
