from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QAbstractListModel, QModelIndex, Qt

from ddl_reminder.domain.deadline import classify_deadline, format_remaining_time
from ddl_reminder.domain.task import Task


class TaskListModel(QAbstractListModel):
    TaskIdRole = int(Qt.UserRole) + 1
    TitleRole = TaskIdRole + 1
    DescriptionRole = TitleRole + 1
    DeadlineTextRole = DescriptionRole + 1
    RemainingTextRole = DeadlineTextRole + 1
    CategoryRole = RemainingTextRole + 1
    CompletedRole = CategoryRole + 1

    _ROLE_NAMES = {
        TaskIdRole: b"taskId",
        TitleRole: b"title",
        DescriptionRole: b"description",
        DeadlineTextRole: b"deadlineText",
        RemainingTextRole: b"remainingText",
        CategoryRole: b"category",
        CompletedRole: b"completed",
    }

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._rows: list[dict[int, object]] = []

    def roleNames(self) -> dict[int, bytes]:
        return self._ROLE_NAMES

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._rows)

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self._rows):
            return None
        return self._rows[index.row()].get(role)

    def replace_tasks(self, tasks: list[Task], now: datetime) -> None:
        rows = []
        for task in tasks:
            if task.is_completed:
                category_value = "completed"
                remaining_text = "已完成"
            else:
                category, _seconds_diff = classify_deadline(task.deadline, now)
                category_value = category.value
                remaining_text = format_remaining_time(task.deadline, now)
            rows.append(
                {
                    self.TaskIdRole: task.id,
                    self.TitleRole: task.title,
                    self.DescriptionRole: task.description or "",
                    self.DeadlineTextRole: task.deadline.strftime("%Y-%m-%d %H:%M"),
                    self.RemainingTextRole: remaining_text,
                    self.CategoryRole: category_value,
                    self.CompletedRole: task.is_completed,
                }
            )

        self.beginResetModel()
        self._rows = rows
        self.endResetModel()
