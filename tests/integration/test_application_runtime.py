import os

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject
from PySide6.QtWidgets import QApplication

from ddl_reminder.application.task_service import TaskService
from ddl_reminder.infrastructure.in_memory_task_repository import InMemoryTaskRepository
from ddl_reminder.main import create_application_runtime


class FakeLock:
    def __init__(self, acquired=True):
        self.acquired = acquired
        self.unlocked = False

    def try_lock(self):
        return self.acquired

    def unlock(self):
        self.unlocked = True


class FakeAutostart:
    def __init__(self):
        self.enabled = False

    def is_enabled(self, _command):
        return self.enabled

    def enable(self, _command):
        self.enabled = True

    def disable(self):
        self.enabled = False


class FakeReminderRunner:
    def __init__(self):
        self.calls = 0

    def run_once(self):
        self.calls += 1


def build_runtime(argv):
    application = QApplication.instance() or QApplication([])
    repository = InMemoryTaskRepository()
    service = TaskService(repository)
    runner = FakeReminderRunner()
    runtime = create_application_runtime(
        argv,
        application=application,
        task_service=service,
        repository=repository,
        autostart=FakeAutostart(),
        instance_lock=FakeLock(),
        reminder_runner=runner,
    )
    application.processEvents()
    return application, runtime, runner


def test_runtime_loads_qml_wires_tray_refresh_and_quit():
    application, runtime, runner = build_runtime(["ddl-reminder"])

    assert runtime is not None
    assert runtime.engine.rootObjects() == [runtime.root]
    floating = runtime.root.findChild(QObject, "floatingWindow")
    assert runtime.root.property("visible") is True
    assert floating.property("visible") is True
    assert runner.calls == 1

    runtime.root.hide()
    runtime.show_main_action.trigger()
    application.processEvents()
    assert runtime.root.property("visible") is True

    runtime.controller.tasksChanged.emit()
    assert runner.calls == 2

    view_refreshes = []
    runtime.controller.viewStateChanged.connect(lambda: view_refreshes.append(True))
    runtime.reminder_timer.timeout.emit()
    assert view_refreshes == [True]
    assert runner.calls == 3

    runtime.quit_action.trigger()
    application.processEvents()
    assert runtime.root.property("visible") is False
    assert floating.property("visible") is False


def test_autostart_launch_shows_only_floating_window():
    application, runtime, _runner = build_runtime(["ddl-reminder", "--autostart"])

    assert runtime is not None
    floating = runtime.root.findChild(QObject, "floatingWindow")
    assert runtime.root.property("visible") is False
    assert floating.property("visible") is True

    runtime.shutdown()
    application.processEvents()


def test_runtime_stops_when_single_instance_lock_is_unavailable():
    application = QApplication.instance() or QApplication([])

    runtime = create_application_runtime(
        ["ddl-reminder"],
        application=application,
        instance_lock=FakeLock(acquired=False),
    )

    assert runtime is None
