import os
from datetime import date, datetime, time

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, QPoint, QRect, QMetaObject
from PySide6.QtTest import QTest
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickItem
from PySide6.QtWidgets import QApplication

from ddl_reminder.application.task_service import TaskService
from ddl_reminder.infrastructure.in_memory_task_repository import InMemoryTaskRepository
from ddl_reminder.ui.app_controller import AppController
from ddl_reminder.ui.floating_window_controller import FloatingWindowController
from ddl_reminder.ui.qml_resources import qml_path


def _find_visual_child(item: QQuickItem, object_name: str):
    for child in item.childItems():
        if child.objectName() == object_name:
            return child
        found = _find_visual_child(child, object_name)
        if found is not None:
            return found
    return None


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
    completed_task = service.create_task(
        title="已完成任务",
        deadline_date=date(2026, 9, 1),
        deadline_time=time(9, 0),
        now=datetime(2026, 8, 30, 12, 0),
    )
    service.complete_task(completed_task.id, datetime(2026, 9, 1, 8, 0))
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
    root.showMainWindow()
    application.processEvents()
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

    sidebar = root.findChild(QObject, "sidebar")
    assert sidebar.property("width") == 238

    assert QMetaObject.invokeMethod(root, "openCreateDialog")
    application.processEvents()
    assert objects["taskEditorDialog"].property("visible") is True
    assert objects["taskEditorDialog"].property("x") == (
        root.property("width") - objects["taskEditorDialog"].property("width")
    ) / 2
    objects["taskEditorDialog"].setProperty("visible", False)

    root.openTaskDetails(task.id)
    application.processEvents()
    assert objects["taskDetailDialog"].property("visible") is True
    assert objects["taskDetailDialog"].property("x") == (
        root.property("width") - objects["taskDetailDialog"].property("width")
    ) / 2
    objects["taskDetailDialog"].setProperty("visible", False)

    controller.setFilter("completed")
    task_list = root.findChild(QObject, "taskList")
    QMetaObject.invokeMethod(task_list, "forceLayout")
    QTest.qWait(50)
    application.processEvents()
    assert task_list.property("count") == 1
    content_item = task_list.property("contentItem")
    task_card = _find_visual_child(content_item, "taskCard")
    status_chip = _find_visual_child(content_item, "taskStatusChip")
    completion_action = _find_visual_child(content_item, "completionAction")
    assert task_card.property("completed") is True
    assert status_chip.property("label") == "已完成"
    assert completion_action.property("visible") is False

    assert QMetaObject.invokeMethod(root, "showFloatingWindow")
    application.processEvents()
    assert objects["floatingWindow"].property("visible") is True
    objects["floatingWindow"].setProperty("visible", False)
    root.close()
