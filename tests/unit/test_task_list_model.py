from datetime import datetime

from PySide6.QtCore import QModelIndex, Qt

from ddl_reminder.domain.task import Task
from ddl_reminder.ui.task_list_model import TaskListModel


def _role(model: TaskListModel, name: bytes) -> int:
    return next(role for role, role_name in model.roleNames().items() if role_name == name)


def test_task_list_model_exposes_qml_safe_role_values():
    model = TaskListModel()
    task = Task(
        id=7,
        title="交作业",
        description=None,
        deadline=datetime(2026, 10, 9, 12, 0),
        created_at=datetime(2026, 10, 7, 8, 0),
        updated_at=datetime(2026, 10, 7, 8, 0),
    )

    model.replace_tasks([task], datetime(2026, 10, 7, 12, 0))

    index = model.index(0, 0, QModelIndex())
    assert model.data(index, _role(model, b"taskId")) == 7
    assert model.data(index, _role(model, b"title")) == "交作业"
    assert model.data(index, _role(model, b"description")) == ""
    assert model.data(index, _role(model, b"deadlineText")) == "2026-10-09 12:00"
    assert model.data(index, _role(model, b"remainingText")) == "剩余2天"
    assert model.data(index, _role(model, b"category")) == "within_three_days"
    assert model.data(index, _role(model, b"completed")) is False


def test_task_list_model_preserves_supplied_order_and_completed_state():
    model = TaskListModel()
    later = Task(
        id=1,
        title="Later",
        deadline=datetime(2026, 10, 8, 12, 0),
        created_at=datetime(2026, 10, 7, 8, 0),
        updated_at=datetime(2026, 10, 7, 8, 0),
    )
    overdue_completed = Task(
        id=2,
        title="Completed",
        deadline=datetime(2026, 10, 7, 11, 0),
        is_completed=True,
        completed_at=datetime(2026, 10, 7, 11, 30),
        created_at=datetime(2026, 10, 7, 9, 0),
        updated_at=datetime(2026, 10, 7, 11, 30),
    )

    model.replace_tasks([later, overdue_completed], datetime(2026, 10, 7, 12, 0))

    title_role = _role(model, b"title")
    completed_role = _role(model, b"completed")
    remaining_role = _role(model, b"remainingText")
    assert model.rowCount(QModelIndex()) == 2
    assert model.data(model.index(0, 0), title_role) == "Later"
    assert model.data(model.index(1, 0), title_role) == "Completed"
    assert model.data(model.index(1, 0), completed_role) is True
    category_role = _role(model, b"category")
    assert model.data(model.index(1, 0), remaining_role) == "已完成"
    assert model.data(model.index(1, 0), category_role) == "completed"
    assert model.data(model.index(0, 0), Qt.DisplayRole) is None
