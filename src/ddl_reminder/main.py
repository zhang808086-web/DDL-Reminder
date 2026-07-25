from __future__ import annotations

import sys
import logging

from PySide6.QtWidgets import QApplication, QMenu, QMessageBox, QSystemTrayIcon
from PySide6.QtGui import QAction, QIcon
from PySide6.QtCore import QTimer



from ddl_reminder.application.task_service import TaskService
from ddl_reminder.infrastructure.database import (
    create_session_factory,
    create_sqlite_engine,
    init_database,
)
from ddl_reminder.infrastructure.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from ddl_reminder.ui.main_window import MainWindow
from ddl_reminder.ui.resources import app_icon_path
from ddl_reminder.ui.theme import apply_codex_font

from ddl_reminder.ui.floating_window import FloatingWindow

from ddl_reminder.application.reminder_runner import ReminderRunner
from ddl_reminder.application.reminder_service import ReminderService
from ddl_reminder.infrastructure.desktop_notifier import DesktopNotifier
from ddl_reminder.infrastructure.single_instance import SingleInstanceLock
from ddl_reminder.infrastructure.app_paths import get_database_path, get_log_path
from ddl_reminder.infrastructure.autostart import (
    WindowsAutostart,
    build_autostart_command,
    is_autostart_launch,
    is_packaged_app,
)

def main() -> int:
    logging.basicConfig(
        filename = get_log_path(),
        level = logging.INFO,
        encoding='utf-8'
    )
    logging.info("DDL-Reminder started")
    app = QApplication(sys.argv)
    apply_codex_font(app)
    app_icon = QIcon(str(app_icon_path()))
    app.setWindowIcon(app_icon)
    
    instance_lock = SingleInstanceLock()
    
    if not instance_lock.try_lock():
        return 0
    
    database_path = get_database_path()
    database_url = f"sqlite:///{database_path.as_posix()}"
    engine = create_sqlite_engine(database_url)
    
    init_database(engine)
    
    session_factory = create_session_factory(engine)
    repository = SQLAlchemyTaskRepository(session_factory)
    task_service = TaskService(repository)
    
    autostart = WindowsAutostart()
    main_window = MainWindow(task_service, autostart)
    floating_window = FloatingWindow(task_service)
    main_window.setWindowIcon(app_icon)
    floating_window.setWindowIcon(app_icon)
    
    def show_main_window() -> None:
        main_window.show()
        main_window.raise_()
        main_window.activateWindow()
        
    def show_floating_window() -> None:
        floating_window.show_from_tray()
    
    main_window.tasks_changed.connect(floating_window.refresh_tasks)
    floating_window.tasks_changed.connect(main_window.refresh_tasks)
    
    tray_icon = QSystemTrayIcon()
    

    
    tray_icon.setIcon(app_icon)
    tray_icon.setToolTip("DDL Reminder")
    
    def handle_tray_activated(reason) -> None:
        if reason == QSystemTrayIcon.DoubleClick:
            show_main_window()
            
    tray_icon.activated.connect(handle_tray_activated)
    
    tray_menu = QMenu()
    show_main_action = QAction("显示主窗口")
    show_main_action.triggered.connect(show_main_window)

    show_floating_action = QAction("显示悬浮窗")
    show_floating_action.triggered.connect(show_floating_window)

    autostart_action = QAction("开机自启")
    autostart_action.setCheckable(True)
    autostart_action.setChecked(autostart.is_enabled(build_autostart_command()))
    autostart_action.setEnabled(is_packaged_app())

    def toggle_autostart(checked: bool) -> None:
        try:
            if checked:
                autostart.enable(build_autostart_command())
                return

            autostart.disable()
        except OSError as error:
            autostart_action.blockSignals(True)
            autostart_action.setChecked(not checked)
            autostart_action.blockSignals(False)
            QMessageBox.warning(main_window, "设置失败", str(error))

    autostart_action.triggered.connect(toggle_autostart)
    main_window.autostart_changed.connect(autostart_action.setChecked)

    quit_action = QAction("退出")
    def quit_application() -> None:
        main_window.allow_close()
        floating_window.allow_close()
        app.quit()

    quit_action.triggered.connect(quit_application)
    tray_menu.addAction(show_main_action)
    tray_menu.addAction(show_floating_action)
    tray_menu.addAction(autostart_action)
    tray_menu.addSeparator()
    tray_menu.addAction(quit_action)

    tray_icon.setContextMenu(tray_menu)
    tray_icon.show()
    
    reminder_service = ReminderService(repository)
    notifier = DesktopNotifier(tray_icon)
    logger = logging.getLogger("ddl_reminder.reminder")
    reminder_runner = ReminderRunner(reminder_service, notifier, logger)

    main_window.tasks_changed.connect(reminder_runner.run_once)
    floating_window.tasks_changed.connect(reminder_runner.run_once)
    reminder_runner.run_once()

    reminder_timer = QTimer()
    reminder_timer.timeout.connect(reminder_runner.run_once)
    reminder_timer.start(30_000)
    

    
    if is_autostart_launch(sys.argv):
        floating_window.show_from_tray()
    else:
        main_window.show()
        floating_window.show()
    
    return app.exec()

if __name__  == "__main__":
    raise SystemExit(main())
    

    
