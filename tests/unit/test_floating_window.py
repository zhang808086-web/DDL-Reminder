import os
from dataclasses import dataclass
from datetime import date, datetime, time

from PySide6.QtWidgets import QApplication, QDialog, QPushButton

from ddl_reminder.domain.task import Task
from ddl_reminder.ui import floating_window as floating_window_module
from ddl_reminder.ui.floating_window import FloatingWindow


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


@dataclass
class FakeDetailData:
    title: str
    description: str
    deadline_date: date
    deadline_time: time


class FakeTaskService:
    def __init__(self) -> None:
        self.updated_task_ids: list[int] = []

    def get_urgent_tasks(self, limit: int = 3) -> list[Task]:
        return []

    def get_task(self, task_id: int) -> Task:
        return Task(
            id=task_id,
            title="Old title",
            description="Old description",
            deadline=datetime(2026, 1, 1, 12, 0),
            created_at=datetime(2026, 1, 1, 9, 0),
            updated_at=datetime(2026, 1, 1, 9, 0),
        )

    def update_task(self, **kwargs) -> Task:
        self.updated_task_ids.append(kwargs["task_id"])
        return self.get_task(kwargs["task_id"])


class CompletingTaskService:
    def __init__(self) -> None:
        self.task = Task(
            id=1,
            title="Urgent task",
            deadline=datetime(2026, 1, 1, 12, 0),
            created_at=datetime(2026, 1, 1, 9, 0),
            updated_at=datetime(2026, 1, 1, 9, 0),
        )
        self.completed_task_ids: list[int] = []

    def get_urgent_tasks(self, limit: int = 3) -> list[Task]:
        if self.task.is_completed:
            return []
        return [self.task]

    def complete_task(self, task_id: int) -> Task:
        self.completed_task_ids.append(task_id)
        self.task.mark_completed(datetime(2026, 1, 1, 10, 0))
        return self.task


class FakeTaskDetailDialog:
    def __init__(self, task: Task, parent=None) -> None:
        self.task = task

    def exec(self) -> int:
        return QDialog.Accepted

    def get_data(self) -> FakeDetailData:
        return FakeDetailData(
            title="New title",
            description="New description",
            deadline_date=date(2026, 1, 2),
            deadline_time=time(13, 30),
        )


def test_floating_window_emits_tasks_changed_after_detail_update(monkeypatch):
    app = QApplication.instance() or QApplication([])
    service = FakeTaskService()
    monkeypatch.setattr(
        floating_window_module,
        "TaskDetailDialog",
        FakeTaskDetailDialog,
    )
    window = FloatingWindow(service)
    emitted = []
    window.tasks_changed.connect(lambda: emitted.append(True))

    window._open_task_detail_by_id(1)

    assert service.updated_task_ids == [1]
    assert emitted == [True]
    window.close()
    app.processEvents()


def test_floating_window_completes_task_from_card_button():
    app = QApplication.instance() or QApplication([])
    service = CompletingTaskService()
    window = FloatingWindow(service)
    emitted = []
    window.tasks_changed.connect(lambda: emitted.append(True))

    card = window.task_cards_layout.itemAt(0).widget()
    complete_button = card.findChild(QPushButton, "completeButton")

    assert complete_button is not None
    complete_button.click()

    assert service.completed_task_ids == [1]
    assert emitted == [True]
    window.close()
    app.processEvents()
