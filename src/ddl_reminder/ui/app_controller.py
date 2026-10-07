from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, time

from PySide6.QtCore import QObject, Property, Signal, Slot

from ddl_reminder.domain.deadline import DeadlineCategory, classify_deadline
from ddl_reminder.domain.exceptions import TaskError
from ddl_reminder.infrastructure.autostart import (
    WindowsAutostart,
    build_autostart_command,
    is_packaged_app,
)
from ddl_reminder.ui.task_list_model import TaskListModel


class AppController(QObject):
    tasksChanged = Signal()
    errorRequested = Signal(str, str)
    autostartChanged = Signal(bool)
    viewStateChanged = Signal()

    def __init__(
        self,
        task_service,
        autostart: WindowsAutostart | None = None,
        *,
        now_provider: Callable[[], datetime] = datetime.now,
        autostart_available: bool | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self.task_service = task_service
        self.autostart = autostart or WindowsAutostart()
        self._now_provider = now_provider
        self._autostart_available = (
            is_packaged_app() if autostart_available is None else autostart_available
        )
        self._autostart_command = build_autostart_command()
        self._current_filter = "active"
        self._search_query = ""
        self._section_title = "进行中"
        self._section_count = 0
        self._main_model = TaskListModel(self)
        self._floating_model = TaskListModel(self)
        try:
            self._autostart_enabled = self._autostart_available and self.autostart.is_enabled(
                self._autostart_command
            )
        except OSError:
            self._autostart_enabled = False
        self.refreshTasks()

    @Property(QObject, constant=True)
    def mainModel(self) -> TaskListModel:
        return self._main_model

    @Property(QObject, constant=True)
    def floatingModel(self) -> TaskListModel:
        return self._floating_model

    @Property(str, notify=viewStateChanged)
    def currentFilter(self) -> str:
        return self._current_filter

    @Property(str, notify=viewStateChanged)
    def sectionTitle(self) -> str:
        return self._section_title

    @Property(int, notify=viewStateChanged)
    def sectionCount(self) -> int:
        return self._section_count

    @Property(bool, notify=autostartChanged)
    def autostartEnabled(self) -> bool:
        return self._autostart_enabled

    @Property(bool, constant=True)
    def autostartAvailable(self) -> bool:
        return self._autostart_available

    @Slot(str)
    def setFilter(self, filter_name: str) -> None:
        if filter_name not in {"active", "completed", "urgent"}:
            return
        self._current_filter = filter_name
        self.refreshTasks()

    @Slot(str)
    def setSearchQuery(self, query: str) -> None:
        self._search_query = query.strip()
        self.refreshTasks()

    @Slot()
    def refreshTasks(self) -> None:
        now = self._now_provider()
        active_tasks = sorted(
            self.task_service.list_active_tasks(),
            key=lambda task: (task.deadline, task.created_at),
        )
        completed_tasks = sorted(
            self.task_service.list_completed_tasks(),
            key=lambda task: (task.deadline, task.created_at),
        )

        tasks = completed_tasks if self._current_filter == "completed" else active_tasks
        if self._current_filter == "urgent":
            tasks = [task for task in tasks if self._is_urgent(task, now)]
        if self._search_query:
            tasks = [
                task
                for task in tasks
                if self._search_query in task.title
                or self._search_query in (task.description or "")
            ]

        self._section_title = {
            "active": "进行中",
            "completed": "已完成",
            "urgent": "紧急",
        }[self._current_filter]
        self._section_count = len(tasks)
        self._main_model.replace_tasks(tasks, now)
        self._floating_model.replace_tasks(active_tasks[:3], now)
        self.viewStateChanged.emit()

    @staticmethod
    def _is_urgent(task, now: datetime) -> bool:
        category, _seconds_diff = classify_deadline(task.deadline, now)
        return category in {
            DeadlineCategory.OVERDUE,
            DeadlineCategory.WITHIN_ONE_HOUR,
            DeadlineCategory.WITHIN_ONE_DAY,
        }

    @Slot(int, result="QVariantMap")
    def taskDetails(self, task_id: int) -> dict[str, object]:
        try:
            task = self.task_service.get_task(task_id)
        except TaskError as error:
            self.errorRequested.emit("读取失败", str(error))
            return {}
        return {
            "taskId": task.id,
            "title": task.title,
            "description": task.description or "",
            "dateText": task.deadline.strftime("%Y-%m-%d"),
            "timeText": task.deadline.strftime("%H:%M"),
            "completed": task.is_completed,
        }

    @Slot(str, str, str, str, result=bool)
    def createTask(
        self,
        title: str,
        description: str,
        date_text: str,
        time_text: str,
    ) -> bool:
        try:
            deadline_date, deadline_time = self._parse_deadline(date_text, time_text)
            self.task_service.create_task(
                title=title,
                description=description,
                deadline_date=deadline_date,
                deadline_time=deadline_time,
                now=self._now_provider(),
            )
        except ValueError:
            self.errorRequested.emit(
                "创建失败",
                "日期或时间格式无效，请使用 YYYY-MM-DD 和 HH:MM。",
            )
            return False
        except TaskError as error:
            self.errorRequested.emit("创建失败", str(error))
            return False
        self._finish_task_change()
        return True

    @Slot(int, str, str, str, str, result=bool)
    def updateTask(
        self,
        task_id: int,
        title: str,
        description: str,
        date_text: str,
        time_text: str,
    ) -> bool:
        try:
            deadline_date, deadline_time = self._parse_deadline(date_text, time_text)
            self.task_service.update_task(
                task_id=task_id,
                title=title,
                description=description,
                deadline_date=deadline_date,
                deadline_time=deadline_time,
                now=self._now_provider(),
            )
        except ValueError:
            self.errorRequested.emit(
                "保存失败",
                "日期或时间格式无效，请使用 YYYY-MM-DD 和 HH:MM。",
            )
            return False
        except TaskError as error:
            self.errorRequested.emit("保存失败", str(error))
            return False
        self._finish_task_change()
        return True

    @Slot(int, result=bool)
    def completeTask(self, task_id: int) -> bool:
        return self._change_task(
            "完成失败",
            lambda: self.task_service.complete_task(task_id, self._now_provider()),
        )

    @Slot(int, result=bool)
    def restoreTask(self, task_id: int) -> bool:
        return self._change_task(
            "恢复失败",
            lambda: self.task_service.restore_task(task_id, self._now_provider()),
        )

    @Slot(int, result=bool)
    def deleteTask(self, task_id: int) -> bool:
        return self._change_task(
            "删除失败",
            lambda: self.task_service.delete_task(task_id),
        )

    @Slot(bool, result=bool)
    def setAutostart(self, enabled: bool) -> bool:
        if not self._autostart_available:
            return False
        try:
            if enabled:
                self.autostart.enable(self._autostart_command)
            else:
                self.autostart.disable()
        except OSError as error:
            self.errorRequested.emit("设置失败", str(error))
            return False
        self._autostart_enabled = enabled
        self.autostartChanged.emit(enabled)
        return True

    @staticmethod
    def _parse_deadline(date_text: str, time_text: str) -> tuple[date, time]:
        return date.fromisoformat(date_text), time.fromisoformat(time_text)

    def _change_task(self, error_title: str, operation: Callable[[], object]) -> bool:
        try:
            operation()
        except TaskError as error:
            self.errorRequested.emit(error_title, str(error))
            return False
        self._finish_task_change()
        return True

    def _finish_task_change(self) -> None:
        self.refreshTasks()
        self.tasksChanged.emit()
