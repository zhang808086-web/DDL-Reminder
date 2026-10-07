from datetime import date, datetime, time

from PySide6.QtCore import QModelIndex

from ddl_reminder.application.task_service import TaskService
from ddl_reminder.infrastructure.in_memory_task_repository import InMemoryTaskRepository
from ddl_reminder.ui.app_controller import AppController


NOW = datetime(2026, 10, 7, 12, 0)


class FakeAutostart:
    def __init__(self, enabled: bool = False, fail: bool = False) -> None:
        self.enabled = enabled
        self.fail = fail
        self.commands: list[str] = []

    def is_enabled(self, expected_command: str | None = None) -> bool:
        return self.enabled

    def enable(self, command: str) -> None:
        if self.fail:
            raise OSError("registry denied")
        self.commands.append(command)
        self.enabled = True

    def disable(self) -> None:
        if self.fail:
            raise OSError("registry denied")
        self.enabled = False


def _model_values(model, role_name: bytes) -> list[object]:
    role = next(role for role, name in model.roleNames().items() if name == role_name)
    return [model.data(model.index(row, 0, QModelIndex()), role) for row in range(model.rowCount())]


def _controller() -> tuple[AppController, TaskService]:
    service = TaskService(InMemoryTaskRepository())
    controller = AppController(
        service,
        FakeAutostart(),
        now_provider=lambda: NOW,
        autostart_available=True,
    )
    return controller, service


def test_controller_orders_active_and_floating_tasks_by_deadline_then_creation():
    controller, service = _controller()
    service.create_task("Fourth", date(2026, 10, 10), now=datetime(2026, 10, 7, 8, 0))
    service.create_task("Second", date(2026, 10, 8), time(18, 0), now=datetime(2026, 10, 7, 9, 0))
    service.create_task("Third", date(2026, 10, 8), time(18, 0), now=datetime(2026, 10, 7, 10, 0))
    service.create_task("First", date(2026, 10, 7), time(13, 0), now=datetime(2026, 10, 7, 11, 0))

    controller.refreshTasks()

    assert _model_values(controller.mainModel, b"title") == ["First", "Second", "Third", "Fourth"]
    assert _model_values(controller.floatingModel, b"title") == ["First", "Second", "Third"]
    assert controller.sectionTitle == "进行中"
    assert controller.sectionCount == 4


def test_controller_filters_completed_and_urgent_tasks():
    controller, service = _controller()
    urgent = service.create_task("Urgent", date(2026, 10, 7), time(13, 0), now=NOW)
    service.create_task("Later", date(2026, 10, 10), now=NOW)
    completed = service.create_task("Done", date(2026, 10, 6), now=NOW)
    service.complete_task(completed.id, NOW)

    controller.setFilter("completed")
    assert _model_values(controller.mainModel, b"taskId") == [completed.id]
    assert controller.sectionTitle == "已完成"

    controller.setFilter("urgent")
    assert _model_values(controller.mainModel, b"taskId") == [urgent.id]
    assert controller.sectionTitle == "紧急"


def test_controller_searches_title_and_description_without_changing_filter():
    controller, service = _controller()
    service.create_task("课程作业", date(2026, 10, 8), description="完成算法题", now=NOW)
    service.create_task("报名", date(2026, 10, 9), description="竞赛提交", now=NOW)

    controller.setSearchQuery("算法")

    assert _model_values(controller.mainModel, b"title") == ["课程作业"]
    assert controller.currentFilter == "active"
    assert controller.sectionCount == 1


def test_controller_creates_task_and_refreshes_both_models():
    controller, service = _controller()
    changes = []
    controller.tasksChanged.connect(lambda: changes.append(True))

    created = controller.createTask("新任务", "描述", "2026-10-08", "14:30")

    assert created is True
    task = service.list_active_tasks()[0]
    assert task.title == "新任务"
    assert task.description == "描述"
    assert task.deadline == datetime(2026, 10, 8, 14, 30)
    assert _model_values(controller.mainModel, b"taskId") == [task.id]
    assert _model_values(controller.floatingModel, b"taskId") == [task.id]
    assert changes == [True]


def test_controller_rejects_malformed_date_without_closing_editor_or_mutating_data():
    controller, service = _controller()
    errors = []
    controller.errorRequested.connect(lambda title, message: errors.append((title, message)))

    created = controller.createTask("新任务", "", "2026-99-08", "14:30")

    assert created is False
    assert service.list_active_tasks() == []
    assert errors == [("创建失败", "日期或时间格式无效，请使用 YYYY-MM-DD 和 HH:MM。")]


def test_controller_surfaces_domain_title_error_without_mutating_data():
    controller, service = _controller()
    errors = []
    controller.errorRequested.connect(lambda title, message: errors.append((title, message)))

    created = controller.createTask("0123456789abcdef", "", "2026-10-08", "14:30")

    assert created is False
    assert service.list_active_tasks() == []
    assert errors == [("创建失败", "Task title cannot be longer than 15 characters")]


def test_controller_updates_task_and_returns_qml_safe_details():
    controller, service = _controller()
    task = service.create_task("旧标题", date(2026, 10, 8), description="旧描述", now=NOW)
    controller.refreshTasks()

    updated = controller.updateTask(task.id, "新标题", "新描述", "2026-10-09", "09:15")

    assert updated is True
    assert controller.taskDetails(task.id) == {
        "taskId": task.id,
        "title": "新标题",
        "description": "新描述",
        "dateText": "2026-10-09",
        "timeText": "09:15",
        "completed": False,
    }


def test_controller_complete_restore_and_delete_refresh_models():
    controller, service = _controller()
    task = service.create_task("任务", date(2026, 10, 8), now=NOW)
    controller.refreshTasks()

    assert controller.completeTask(task.id) is True
    assert _model_values(controller.mainModel, b"taskId") == []
    assert _model_values(controller.floatingModel, b"taskId") == []

    controller.setFilter("completed")
    assert _model_values(controller.mainModel, b"taskId") == [task.id]
    assert controller.restoreTask(task.id) is True
    assert _model_values(controller.mainModel, b"taskId") == []

    controller.setFilter("active")
    assert _model_values(controller.mainModel, b"taskId") == [task.id]
    assert controller.deleteTask(task.id) is True
    assert _model_values(controller.mainModel, b"taskId") == []


def test_controller_rolls_back_autostart_view_state_when_registry_write_fails():
    service = TaskService(InMemoryTaskRepository())
    autostart = FakeAutostart(enabled=False, fail=True)
    controller = AppController(
        service,
        autostart,
        now_provider=lambda: NOW,
        autostart_available=True,
    )
    errors = []
    controller.errorRequested.connect(lambda title, message: errors.append((title, message)))

    changed = controller.setAutostart(True)

    assert changed is False
    assert controller.autostartEnabled is False
    assert errors == [("设置失败", "registry denied")]
