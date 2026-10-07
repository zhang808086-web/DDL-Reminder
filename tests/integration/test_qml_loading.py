import os
from datetime import datetime

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWidgets import QApplication

from ddl_reminder.application.task_service import TaskService
from ddl_reminder.infrastructure.in_memory_task_repository import InMemoryTaskRepository
from ddl_reminder.ui.app_controller import AppController
from ddl_reminder.ui.floating_window_controller import FloatingWindowController
from ddl_reminder.ui.qml_resources import qml_path


def test_main_qml_loads_with_required_shell_objects_and_root_api():
    application = QApplication.instance() or QApplication([])
    service = TaskService(InMemoryTaskRepository())
    controller = AppController(
        service,
        now_provider=lambda: datetime(2026, 10, 7, 12, 0),
        autostart_available=False,
    )
    floating_controller = FloatingWindowController()
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appController", controller)
    engine.rootContext().setContextProperty(
        "floatingWindowController", floating_controller
    )

    warnings = []
    engine.warnings.connect(lambda messages: warnings.extend(messages))
    engine.load(str(qml_path("Main.qml")))
    application.processEvents()

    assert len(engine.rootObjects()) == 1, [warning.toString() for warning in warnings]
    assert warnings == []
    root = engine.rootObjects()[0]
    assert root.objectName() == "mainWindow"
    for name in ("sidebar", "searchField", "createTaskButton", "taskList"):
        assert root.findChild(QObject, name) is not None
    methods = {root.metaObject().method(index).name().data().decode() for index in range(root.metaObject().methodCount())}
    assert {"showMainWindow", "showFloatingWindow", "prepareToQuit"} <= methods
    root.close()
