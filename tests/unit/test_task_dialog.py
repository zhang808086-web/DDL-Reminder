import os
from datetime import time

from PySide6.QtWidgets import QApplication

from ddl_reminder.ui.task_dialog import TaskDialog


os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def test_task_dialog_returns_default_deadline_time():
    app = QApplication.instance() or QApplication([])
    dialog = TaskDialog()

    data = dialog.get_data()

    assert data.deadline_time == time(23, 59)
    dialog.close()
    app.processEvents()
