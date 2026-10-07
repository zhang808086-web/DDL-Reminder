import os
from datetime import date, datetime, time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, QPoint, QRect, QMetaObject
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
    task = service.create_task(
        title="发布新版",
        description="验证 QML 安装包",
        deadline_date=date(2026, 10, 8),
        deadline_time=time(18, 30),
        now=datetime(2026, 10, 7, 12, 0),
    )
    controller = AppController(
        service,
        now_provider=lambda: datetime(2026, 10, 7, 12, 0),
        autostart_available=False,
    )
    class MemorySettings:
        def __init__(self):
            self.position = None

        def value(self, _key):
            return self.position

        def setValue(self, _key, value):
            self.position = QPoint(value)

    floating_controller = FloatingWindowController(
        settings=MemorySettings(),
        screen_geometry_provider=lambda _window: QRect(0, 0, 1920, 1080),
    )
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
    methods = {
        root.metaObject().method(index).name().data().decode()
        for index in range(root.metaObject().methodCount())
    }
    assert {
        "showMainWindow",
        "showFloatingWindow",
        "prepareToQuit",
        "openCreateDialog",
        "openTaskDetails",
        "openSettings",
    } <= methods

    expected_objects = (
        "taskEditorDialog",
        "taskDetailDialog",
        "settingsDialog",
        "confirmDialog",
        "floatingWindow",
    )
    objects = {name: root.findChild(QObject, name) for name in expected_objects}
    assert all(objects.values())

    assert QMetaObject.invokeMethod(root, "openCreateDialog")
    application.processEvents()
    assert objects["taskEditorDialog"].property("visible") is True
    objects["taskEditorDialog"].setProperty("visible", False)

    root.openTaskDetails(task.id)
    application.processEvents()
    assert objects["taskDetailDialog"].property("visible") is True
    objects["taskDetailDialog"].setProperty("visible", False)

    assert QMetaObject.invokeMethod(root, "showFloatingWindow")
    application.processEvents()
    assert objects["floatingWindow"].property("visible") is True
    objects["floatingWindow"].setProperty("visible", False)
    root.close()
