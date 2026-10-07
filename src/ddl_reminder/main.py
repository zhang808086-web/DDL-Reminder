from __future__ import annotations

import logging
import sys

from PySide6.QtCore import QTimer
from PySide6.QtGui import QAction, QIcon
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

from ddl_reminder.application.reminder_runner import ReminderRunner
from ddl_reminder.application.reminder_service import ReminderService
from ddl_reminder.application.task_service import TaskService
from ddl_reminder.infrastructure.app_paths import get_database_path, get_log_path
from ddl_reminder.infrastructure.autostart import WindowsAutostart, is_autostart_launch
from ddl_reminder.infrastructure.database import (
    create_session_factory,
    create_sqlite_engine,
    init_database,
)
from ddl_reminder.infrastructure.desktop_notifier import DesktopNotifier
from ddl_reminder.infrastructure.single_instance import SingleInstanceLock
from ddl_reminder.infrastructure.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from ddl_reminder.ui.app_controller import AppController
from ddl_reminder.ui.floating_window_controller import FloatingWindowController
from ddl_reminder.ui.qml_resources import qml_path
from ddl_reminder.ui.resources import app_icon_path


class ApplicationRuntime:
    """Own every long-lived Qt and application object for one process."""

    def __init__(
        self,
        *,
        application,
        engine,
        controller,
        floating_controller,
        root,
        tray_icon,
        tray_menu,
        show_main_action,
        show_floating_action,
        autostart_action,
        quit_action,
        reminder_runner,
        reminder_timer,
        instance_lock,
        database_engine=None,
    ) -> None:
        self.application = application
        self.engine = engine
        self.controller = controller
        self.floating_controller = floating_controller
        self.root = root
        self.tray_icon = tray_icon
        self.tray_menu = tray_menu
        self.show_main_action = show_main_action
        self.show_floating_action = show_floating_action
        self.autostart_action = autostart_action
        self.quit_action = quit_action
        self.reminder_runner = reminder_runner
        self.reminder_timer = reminder_timer
        self.instance_lock = instance_lock
        self.database_engine = database_engine
        self._shut_down = False

    def show_main_window(self) -> None:
        self.root.showMainWindow()

    def show_floating_window(self) -> None:
        self.root.showFloatingWindow()

    def quit(self) -> None:
        self.shutdown()
        self.application.quit()

    def shutdown(self) -> None:
        if self._shut_down:
            return
        self._shut_down = True
        self.reminder_timer.stop()
        self.root.prepareToQuit()
        self.tray_icon.hide()
        self.instance_lock.unlock()


def _build_database_service():
    database_path = get_database_path()
    database_url = f"sqlite:///{database_path.as_posix()}"
    engine = create_sqlite_engine(database_url)
    init_database(engine)
    session_factory = create_session_factory(engine)
    repository = SQLAlchemyTaskRepository(session_factory)
    return engine, repository, TaskService(repository)


def create_application_runtime(
    argv: list[str],
    *,
    application: QApplication | None = None,
    task_service: TaskService | None = None,
    repository=None,
    autostart: WindowsAutostart | None = None,
    instance_lock=None,
    reminder_runner=None,
) -> ApplicationRuntime | None:
    app = application or QApplication(argv)
    app.setQuitOnLastWindowClosed(False)
    app_icon = QIcon(str(app_icon_path()))
    app.setWindowIcon(app_icon)

    lock = instance_lock or SingleInstanceLock()
    if not lock.try_lock():
        return None

    database_engine = None
    if task_service is None:
        database_engine, repository, task_service = _build_database_service()
    elif repository is None:
        repository = task_service.repo

    autostart_service = autostart or WindowsAutostart()
    controller = AppController(task_service, autostart_service)
    floating_controller = FloatingWindowController()

    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appController", controller)
    engine.rootContext().setContextProperty(
        "floatingWindowController", floating_controller
    )
    engine.load(str(qml_path("Main.qml")))
    if not engine.rootObjects():
        lock.unlock()
        raise RuntimeError("Unable to load the QML application root")
    root = engine.rootObjects()[0]
    root.setIcon(app_icon)

    tray_icon = QSystemTrayIcon(app_icon)
    tray_icon.setToolTip("DDL Reminder")
    tray_menu = QMenu()
    show_main_action = tray_menu.addAction("显示主窗口")
    show_floating_action = tray_menu.addAction("显示悬浮窗")
    autostart_action = tray_menu.addAction("开机自启")
    autostart_action.setCheckable(True)
    autostart_action.setChecked(controller.autostartEnabled)
    autostart_action.setEnabled(controller.autostartAvailable)
    tray_menu.addSeparator()
    quit_action = tray_menu.addAction("退出")
    tray_icon.setContextMenu(tray_menu)

    if reminder_runner is None:
        notifier = DesktopNotifier(tray_icon)
        reminder_service = ReminderService(repository)
        reminder_runner = ReminderRunner(
            reminder_service,
            notifier,
            logging.getLogger("ddl_reminder.reminder"),
        )

    reminder_timer = QTimer()
    reminder_timer.timeout.connect(reminder_runner.run_once)
    reminder_timer.start(30_000)

    runtime = ApplicationRuntime(
        application=app,
        engine=engine,
        controller=controller,
        floating_controller=floating_controller,
        root=root,
        tray_icon=tray_icon,
        tray_menu=tray_menu,
        show_main_action=show_main_action,
        show_floating_action=show_floating_action,
        autostart_action=autostart_action,
        quit_action=quit_action,
        reminder_runner=reminder_runner,
        reminder_timer=reminder_timer,
        instance_lock=lock,
        database_engine=database_engine,
    )

    show_main_action.triggered.connect(runtime.show_main_window)
    show_floating_action.triggered.connect(runtime.show_floating_window)
    autostart_action.triggered.connect(controller.setAutostart)
    controller.autostartChanged.connect(autostart_action.setChecked)
    controller.tasksChanged.connect(reminder_runner.run_once)
    quit_action.triggered.connect(runtime.quit)
    tray_icon.activated.connect(
        lambda reason: runtime.show_main_window()
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick
        else None
    )
    app.aboutToQuit.connect(runtime.shutdown)

    tray_icon.show()
    reminder_runner.run_once()
    if is_autostart_launch(argv):
        runtime.show_floating_window()
    else:
        runtime.show_main_window()
        runtime.show_floating_window()
    return runtime


def main() -> int:
    logging.basicConfig(
        filename=get_log_path(),
        level=logging.INFO,
        encoding="utf-8",
    )
    logging.info("DDL-Reminder started")
    app = QApplication(sys.argv)
    try:
        runtime = create_application_runtime(sys.argv, application=app)
    except RuntimeError:
        logging.exception("Failed to initialize QML application")
        return 1
    if runtime is None:
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
