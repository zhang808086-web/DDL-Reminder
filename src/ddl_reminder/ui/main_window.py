from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QPoint, Qt, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ddl_reminder.domain.deadline import DeadlineCategory, classify_deadline
from ddl_reminder.domain.exceptions import TaskError
from ddl_reminder.infrastructure.autostart import WindowsAutostart
from ddl_reminder.ui.confirm_dialog import ask_confirm
from ddl_reminder.ui.settings_dialog import SettingsDialog
from ddl_reminder.ui.task_detail_dialog import TaskDetailDialog
from ddl_reminder.ui.task_dialog import TaskDialog
from ddl_reminder.ui.task_list_item import TaskListItem
from ddl_reminder.ui.theme import (
    CODEX_CJK_QSS_FONT_FAMILY,
    CODEX_QSS_FONT_FAMILY,
)
from ddl_reminder.ui.window_control_button import WindowControlButton


class MainWindow(QMainWindow):
    tasks_changed = Signal()
    autostart_changed = Signal(bool)

    def __init__(self, task_service, autostart: WindowsAutostart | None = None):
        super().__init__()
        self.task_service = task_service
        self.autostart = autostart or WindowsAutostart()
        self._allow_close = False
        self._drag_offset: QPoint | None = None
        self.current_filter = "active"

        self.setWindowTitle("DDL Reminder")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(900, 600)
        self._setup_ui()

    def _setup_ui(self) -> None:
        central = QWidget()
        central.setObjectName("transparentRoot")
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("mainShell")
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(28)
        shadow.setOffset(0, 8)
        shadow.setColor(QColor(20, 32, 44, 55))
        shell.setGraphicsEffect(shadow)
        root_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(22, 18, 22, 22)
        shell_layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(10)

        title_label = QLabel("DDL Reminder")
        title_label.setObjectName("windowTitle")

        self.search_input = QLineEdit()
        self.search_input.setObjectName("searchInput")
        self.search_input.setPlaceholderText("搜索任务")
        self.search_input.textChanged.connect(self.refresh_tasks)

        self.create_btn = QPushButton("+ 新建任务")
        self.create_btn.setObjectName("primaryButton")
        self.create_btn.clicked.connect(self._open_create_dialog)

        minimize_btn = WindowControlButton("minimize")
        minimize_btn.setToolTip("最小化")
        minimize_btn.clicked.connect(self.showMinimized)

        maximize_btn = WindowControlButton("maximize")
        maximize_btn.setToolTip("最大化/还原")
        maximize_btn.clicked.connect(self._toggle_maximized)

        close_btn = WindowControlButton("close")
        close_btn.setToolTip("隐藏主窗口")
        close_btn.clicked.connect(self.hide)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.search_input)
        header_layout.addWidget(self.create_btn)
        header_layout.addWidget(minimize_btn)
        header_layout.addWidget(maximize_btn)
        header_layout.addWidget(close_btn)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(14)

        self.sidebar = QFrame()
        self.sidebar.setObjectName("glassPanel")
        self.sidebar.setFixedWidth(190)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(12, 18, 12, 18)
        sidebar_layout.setSpacing(10)

        self.active_btn = self._create_filter_button("进行中", "active")
        self.completed_btn = self._create_filter_button("已完成", "completed")
        self.urgent_btn = self._create_filter_button("紧急", "urgent")

        sidebar_layout.addWidget(self.active_btn)
        sidebar_layout.addWidget(self.completed_btn)
        sidebar_layout.addWidget(self.urgent_btn)
        sidebar_layout.addStretch()

        self.settings_btn = self._create_settings_button()
        sidebar_layout.addWidget(self.settings_btn)

        list_panel = QFrame()
        list_panel.setObjectName("glassPanel")
        list_panel_layout = QVBoxLayout(list_panel)
        list_panel_layout.setContentsMargins(24, 24, 24, 24)
        list_panel_layout.setSpacing(16)

        list_header_layout = QHBoxLayout()
        list_header_layout.setContentsMargins(0, 0, 0, 0)
        list_header_layout.setSpacing(8)

        self.section_title = QLabel("进行中")
        self.section_title.setObjectName("sectionTitle")
        self.section_count = QLabel("0")
        self.section_count.setObjectName("countBadge")

        list_header_layout.addWidget(self.section_title)
        list_header_layout.addWidget(self.section_count)
        list_header_layout.addStretch()

        self.scroll_area = QScrollArea()
        self.scroll_area.setObjectName("taskScrollArea")
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scrollContent")
        self.list_content = QVBoxLayout(self.scroll_content)
        self.list_content.setContentsMargins(0, 0, 0, 0)
        self.list_content.setSpacing(12)
        self.scroll_area.setWidget(self.scroll_content)

        list_panel_layout.addLayout(list_header_layout)
        list_panel_layout.addWidget(self.scroll_area, 1)

        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(list_panel, 1)

        shell_layout.addLayout(header_layout)
        shell_layout.addLayout(content_layout, 1)

        self._apply_styles()
        self._update_filter_buttons()
        self.refresh_tasks()

    def _create_filter_button(self, text: str, filter_name: str) -> QToolButton:
        button = QToolButton()
        button.setText(text)
        button.setObjectName("filterButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedHeight(48)
        button.clicked.connect(lambda: self._set_filter(filter_name))
        return button

    def _create_settings_button(self) -> QToolButton:
        button = QToolButton()
        button.setText("设置")
        button.setObjectName("settingsButton")
        button.setCursor(Qt.PointingHandCursor)
        button.setFixedHeight(44)
        button.clicked.connect(self._open_settings)
        return button

    def _toggle_maximized(self) -> None:
        if self.isMaximized():
            self.showNormal()
            return

        self.showMaximized()

    def _apply_styles(self) -> None:
        stylesheet = """
            QWidget#transparentRoot {
                background-color: transparent;
                font-family: __CODEX_FONT__;
            }

            QFrame#mainShell {
                background-color: rgba(234, 243, 250, 210);
                border: 1px solid rgba(255, 255, 255, 185);
                border-radius: 28px;
            }

            QFrame#glassPanel {
                background-color: rgba(255, 255, 255, 105);
                border: 1px solid rgba(255, 255, 255, 155);
                border-radius: 18px;
            }

            QLabel#windowTitle {
                color: #26313D;
                font-family: __CODEX_FONT__;
                font-size: 21px;
                font-weight: 600;
            }

            QLineEdit#searchInput {
                min-width: 210px;
                min-height: 34px;
                padding: 0 14px;
                background-color: rgba(255, 255, 255, 135);
                border: 1px solid rgba(255, 255, 255, 165);
                border-radius: 17px;
                color: #26313D;
                font-family: __CODEX_FONT__;
                font-size: 14px;
            }

            QPushButton#primaryButton {
                min-height: 34px;
                padding: 0 14px;
                background-color: #2563EB;
                border: none;
                border-radius: 9px;
                color: white;
                font-family: __CODEX_CJK_FONT__;
                font-size: 14px;
                font-weight: 500;
            }

            QPushButton#primaryButton:hover {
                background-color: #1D4ED8;
            }

            QToolButton#windowButton,
            QToolButton#closeWindowButton {
                background-color: rgba(255, 255, 255, 35);
                border: 1px solid rgba(38, 49, 61, 80);
                border-radius: 8px;
                color: rgba(31, 41, 51, 175);
            }

            QToolButton#windowButton:hover {
                background-color: rgba(255, 255, 255, 120);
                border-color: rgba(38, 49, 61, 115);
                color: #26313D;
            }

            QToolButton#closeWindowButton:hover {
                background-color: rgba(232, 93, 93, 35);
                border-color: rgba(232, 93, 93, 150);
                color: #D93636;
            }

            QToolButton#filterButton {
                padding: 0 14px;
                background-color: transparent;
                border: none;
                border-radius: 12px;
                color: rgba(38, 49, 61, 170);
                font-family: __CODEX_FONT__;
                font-size: 15px;
                font-weight: 500;
                text-align: left;
            }

            QToolButton#filterButton[active="true"] {
                background-color: rgba(255, 255, 255, 145);
                color: #2563EB;
                border-left: 4px solid #3B82F6;
            }

            QToolButton#settingsButton {
                padding: 0 14px;
                background-color: rgba(255, 255, 255, 70);
                border: 1px solid rgba(115, 132, 153, 46);
                border-radius: 12px;
                color: rgba(38, 49, 61, 170);
                font-family: __CODEX_CJK_FONT__;
                font-size: 14px;
                font-weight: 500;
                text-align: left;
            }

            QToolButton#settingsButton:hover {
                background-color: rgba(255, 255, 255, 130);
                border-color: rgba(115, 132, 153, 80);
                color: #2563EB;
            }

            QLabel#sectionTitle {
                color: #26313D;
                font-family: __CODEX_FONT__;
                font-size: 17px;
                font-weight: 600;
            }

            QLabel#countBadge {
                min-width: 28px;
                min-height: 24px;
                padding: 0 8px;
                background-color: rgba(255, 255, 255, 135);
                border-radius: 12px;
                color: #3B82F6;
                font-family: __CODEX_FONT__;
                font-size: 13px;
                font-weight: 500;
            }

            QLabel#emptyText {
                color: rgba(38, 49, 61, 135);
                font-family: __CODEX_FONT__;
                font-size: 24px;
                font-weight: 400;
            }

            QScrollArea#taskScrollArea,
            QScrollArea#taskScrollArea QWidget#scrollContent,
            QScrollArea#taskScrollArea > QWidget,
            QScrollArea#taskScrollArea > QWidget > QWidget {
                background-color: transparent;
                border: none;
            }

            QScrollBar:vertical {
                width: 12px;
                background: transparent;
                border: none;
                margin: 10px 2px 10px 2px;
            }

            QScrollBar::handle:vertical {
                min-height: 64px;
                background: rgba(38, 49, 61, 42);
                border-radius: 4px;
            }

            QScrollBar::handle:vertical:hover {
                background: rgba(38, 49, 61, 72);
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
                background: transparent;
                border: none;
            }

            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background: transparent;
            }
            """
        self.setStyleSheet(
            stylesheet.replace("__CODEX_FONT__", CODEX_QSS_FONT_FAMILY).replace(
                "__CODEX_CJK_FONT__", CODEX_CJK_QSS_FONT_FAMILY
            )
        )
        self.scroll_area.viewport().setAutoFillBackground(False)

    def _set_filter(self, filter_name: str) -> None:
        self.current_filter = filter_name
        self._update_filter_buttons()
        self.refresh_tasks()

    def _open_settings(self) -> None:
        dialog = SettingsDialog(self.autostart, self)
        dialog.autostart_changed.connect(self.autostart_changed)
        dialog.exec()

    def _update_filter_buttons(self) -> None:
        buttons = {
            "active": self.active_btn,
            "completed": self.completed_btn,
            "urgent": self.urgent_btn,
        }

        for filter_name, button in buttons.items():
            button.setProperty("active", filter_name == self.current_filter)
            button.style().unpolish(button)
            button.style().polish(button)

    def _open_create_dialog(self) -> None:
        dialog = TaskDialog(self)

        while True:
            if dialog.exec() != QDialog.Accepted:
                return

            data = dialog.get_data()

            try:
                self.task_service.create_task(
                    title=data.title,
                    description=data.description,
                    deadline_date=data.deadline_date,
                    deadline_time=data.deadline_time,
                )
            except TaskError as error:
                QMessageBox.warning(dialog, "创建失败", str(error))
                continue

            self._refresh_all_tasks()
            self.tasks_changed.emit()
            return

    def _refresh_all_tasks(self) -> None:
        self.refresh_tasks()

    def refresh_tasks(self) -> None:
        self._clear_task_items()

        now = datetime.now()
        tasks = self._tasks_for_current_filter(now)
        completed = self.current_filter == "completed"

        self.section_title.setText(self._title_for_current_filter())
        self.section_count.setText(str(len(tasks)))

        if not tasks:
            empty_label = QLabel("暂无任务")
            empty_label.setObjectName("emptyText")
            empty_label.setAlignment(Qt.AlignCenter)
            self.list_content.addStretch(1)
            self.list_content.addWidget(empty_label, 0, Qt.AlignCenter)
            self.list_content.addStretch(1)
            return

        for task in tasks:
            item = TaskListItem(task, now, completed=completed)
            item.clicked.connect(self._open_task_detail)
            item.complete_clicked.connect(self._handle_complete_or_restore)
            item.edit_clicked.connect(self._open_task_detail)
            item.delete_clicked.connect(self._delete_task)
            self.list_content.addWidget(item)

        self.list_content.addStretch()

    def _tasks_for_current_filter(self, now: datetime):
        if self.current_filter == "completed":
            tasks = self.task_service.list_completed_tasks()
        else:
            tasks = self.task_service.list_active_tasks()

        if self.current_filter == "urgent":
            tasks = [task for task in tasks if self._is_urgent(task, now)]

        query = self.search_input.text().strip()
        if query:
            tasks = [
                task
                for task in tasks
                if query in task.title or query in (task.description or "")
            ]

        return tasks

    def _is_urgent(self, task, now: datetime) -> bool:
        category, _seconds_diff = classify_deadline(task.deadline, now)
        return category in {
            DeadlineCategory.OVERDUE,
            DeadlineCategory.WITHIN_ONE_HOUR,
            DeadlineCategory.WITHIN_ONE_DAY,
        }

    def _title_for_current_filter(self) -> str:
        if self.current_filter == "completed":
            return "已完成"
        if self.current_filter == "urgent":
            return "紧急"
        return "进行中"

    def _handle_complete_or_restore(self, task_id: int) -> None:
        if self.current_filter == "completed":
            self._restore_task(task_id)
            return

        self._complete_task(task_id)

    def _complete_task(self, task_id: int) -> None:
        self.task_service.complete_task(task_id)
        self._refresh_all_tasks()
        self.tasks_changed.emit()

    def _restore_task(self, task_id: int) -> None:
        if not ask_confirm("restore", self):
            return

        self.task_service.restore_task(task_id)
        self._refresh_all_tasks()
        self.tasks_changed.emit()

    def _delete_task(self, task_id: int) -> None:
        if not ask_confirm("delete", self):
            return

        self.task_service.delete_task(task_id)
        self._refresh_all_tasks()
        self.tasks_changed.emit()

    def _open_task_detail(self, task_id: int) -> None:
        task = self.task_service.get_task(task_id)
        dialog = TaskDetailDialog(task, self)

        while True:
            if dialog.exec() != QDialog.Accepted:
                return

            data = dialog.get_data()

            try:
                self.task_service.update_task(
                    task_id=task_id,
                    title=data.title,
                    description=data.description,
                    deadline_date=data.deadline_date,
                    deadline_time=data.deadline_time,
                )
            except TaskError as error:
                QMessageBox.warning(dialog, "保存失败", str(error))
                dialog._set_editing(True)
                continue

            self._refresh_all_tasks()
            self.tasks_changed.emit()
            return

    def _clear_task_items(self) -> None:
        while self.list_content.count():
            item = self.list_content.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)

    def allow_close(self) -> None:
        self._allow_close = True

    def closeEvent(self, event) -> None:
        if self._allow_close:
            super().closeEvent(event)
            return

        event.ignore()
        self.hide()
