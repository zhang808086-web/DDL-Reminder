from __future__ import annotations

import sys
from datetime import date, datetime, time
from pathlib import Path

from PySide6.QtCore import QObject, QPoint, QRect
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtQuick import QQuickWindow
from PySide6.QtWidgets import QApplication
from shiboken6 import getCppPointer, wrapInstance

from ddl_reminder.application.task_service import TaskService
from ddl_reminder.infrastructure.in_memory_task_repository import InMemoryTaskRepository
from ddl_reminder.ui.app_controller import AppController
from ddl_reminder.ui.floating_window_controller import FloatingWindowController
from ddl_reminder.ui.qml_resources import qml_path


NOW = datetime(2026, 10, 7, 14, 30)
OUTPUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "screenshots"


class MemorySettings:
    def __init__(self) -> None:
        self.position = QPoint(1480, 160)

    def value(self, _key):
        return self.position

    def setValue(self, _key, value) -> None:
        self.position = QPoint(value)


def add_tasks(service: TaskService) -> list[int]:
    task_ids = []
    samples = [
        ("提交毕业设计中期报告", "整理实验结果与进度说明", date(2026, 10, 7), time(16, 0)),
        ("软件工程小组演示", "确认演示流程并上传最终版本", date(2026, 10, 8), time(10, 30)),
        ("机器学习课程作业", "完成模型对比与误差分析", date(2026, 10, 10), time(23, 59)),
        ("更新项目技术文档", "补充部署步骤和架构图", date(2026, 10, 14), time(18, 0)),
    ]
    for title, description, deadline_date, deadline_time in samples:
        task = service.create_task(
            title=title,
            description=description,
            deadline_date=deadline_date,
            deadline_time=deadline_time,
            now=NOW,
        )
        task_ids.append(task.id)
    service.complete_task(task_ids[-1], NOW)
    return task_ids


def settle(application: QApplication, frames: int = 8) -> None:
    for _ in range(frames):
        application.processEvents()


def save_window(window, filename: str) -> None:
    quick_window = wrapInstance(getCppPointer(window)[0], QQuickWindow)
    image = quick_window.grabWindow()
    if image.isNull():
        raise RuntimeError(f"Unable to capture {filename}")
    target = OUTPUT_DIR / filename
    if not image.save(str(target)):
        raise RuntimeError(f"Unable to save {target}")


def main() -> int:
    application = QApplication(sys.argv)
    service = TaskService(InMemoryTaskRepository())
    task_ids = add_tasks(service)
    controller = AppController(
        service,
        now_provider=lambda: NOW,
        autostart_available=False,
    )
    floating_controller = FloatingWindowController(
        settings=MemorySettings(),
        screen_geometry_provider=lambda _window: QRect(0, 0, 1920, 1080),
    )
    engine = QQmlApplicationEngine()
    engine.rootContext().setContextProperty("appController", controller)
    engine.rootContext().setContextProperty(
        "floatingWindowController", floating_controller
    )
    engine.load(str(qml_path("Main.qml")))
    if not engine.rootObjects():
        raise RuntimeError("Main.qml did not load")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    root = engine.rootObjects()[0]
    floating = root.findChild(QObject, "floatingWindow")
    detail = root.findChild(QObject, "taskDetailDialog")

    root.showMainWindow()
    settle(application)
    save_window(root, "main-window.png")

    controller.setFilter("completed")
    settle(application)
    save_window(root, "completed-tasks.png")
    root.openTaskDetails(task_ids[-1])
    settle(application)
    save_window(root, "completed-task-detail.png")
    detail.setProperty("visible", False)
    controller.setFilter("active")
    settle(application)

    root.showFloatingWindow()
    settle(application)
    save_window(floating, "floating-window.png")
    floating.setProperty("visible", False)

    root.openTaskDetails(task_ids[1])
    settle(application)
    save_window(root, "task-detail-dialog.png")

    detail.setProperty("visible", False)
    root.prepareToQuit()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
