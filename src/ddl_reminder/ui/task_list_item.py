from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from ddl_reminder.domain.deadline import (
    DeadlineCategory,
    classify_deadline,
    format_remaining_time,
)
from ddl_reminder.ui.theme import CODEX_QSS_FONT_FAMILY, CODEX_SYMBOL_QSS_FONT_FAMILY


class TaskListItem(QFrame):
    clicked = Signal(int)
    complete_clicked = Signal(int)
    edit_clicked = Signal(int)
    delete_clicked = Signal(int)

    def __init__(self, task, now: datetime, completed: bool = False, parent=None) -> None:
        super().__init__(parent)
        self.task = task
        self.task_id = task.id
        self.completed = completed
        self._setup_ui(now)

    def _setup_ui(self, now: datetime) -> None:
        category, _seconds_diff = classify_deadline(self.task.deadline, now)
        color = self._color_for_category(category, self.completed)
        remaining_text = "已完成" if self.completed else format_remaining_time(self.task.deadline, now)

        self.setObjectName("taskListItem")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedHeight(86)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        color_bar = QWidget()
        color_bar.setFixedWidth(4)
        color_bar.setStyleSheet(
            f"""
            QWidget {{
                background-color: {color};
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            }}
            """
        )
        root_layout.addWidget(color_bar)

        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(18, 12, 16, 12)
        body_layout.setSpacing(18)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(6)

        title_label = QLabel(self.task.title)
        title_label.setObjectName("taskTitle")

        description_label = QLabel(self.task.description or "无描述")
        description_label.setObjectName("taskDescription")

        text_layout.addWidget(title_label)
        text_layout.addWidget(description_label)

        time_layout = QVBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(6)

        status_label = QLabel(f"◷ {remaining_text}")
        status_label.setObjectName("taskStatus")
        status_label.setStyleSheet(
            f"""
            QLabel#taskStatus {{
                color: {color};
                font-family: {CODEX_QSS_FONT_FAMILY};
                font-size: 14px;
                font-weight: 600;
            }}
            """
        )

        deadline_label = QLabel(self.task.deadline.strftime("%Y-%m-%d %H:%M"))
        deadline_label.setObjectName("taskDeadline")

        time_layout.addWidget(status_label)
        time_layout.addWidget(deadline_label)

        actions_layout = QHBoxLayout()
        actions_layout.setContentsMargins(0, 0, 0, 0)
        actions_layout.setSpacing(8)

        complete_button = self._icon_button("↩" if self.completed else "✓")
        edit_button = self._icon_button("✎")
        delete_button = self._icon_button("×")

        complete_button.setToolTip("恢复任务" if self.completed else "完成任务")
        edit_button.setToolTip("编辑任务")
        delete_button.setToolTip("删除任务")

        complete_button.clicked.connect(lambda: self.complete_clicked.emit(self.task_id))
        edit_button.clicked.connect(lambda: self.edit_clicked.emit(self.task_id))
        delete_button.clicked.connect(lambda: self.delete_clicked.emit(self.task_id))

        actions_layout.addWidget(complete_button)
        actions_layout.addWidget(edit_button)
        actions_layout.addWidget(delete_button)

        body_layout.addLayout(text_layout, 1)
        body_layout.addLayout(time_layout)
        body_layout.addLayout(actions_layout)

        root_layout.addLayout(body_layout, 1)

        stylesheet = """
            QFrame#taskListItem {
                background-color: rgba(255, 255, 255, 165);
                border: 1px solid rgba(255, 255, 255, 150);
                border-radius: 12px;
                font-family: __CODEX_FONT__;
            }

            QFrame#taskListItem:hover {
                background-color: rgba(255, 255, 255, 205);
            }

            QLabel#taskTitle {
                color: #26313D;
                font-family: __CODEX_FONT__;
                font-size: 15px;
                font-weight: 600;
            }

            QLabel#taskDescription,
            QLabel#taskDeadline {
                color: rgba(38, 49, 61, 150);
                font-family: __CODEX_FONT__;
                font-size: 12px;
            }
            """
        self.setStyleSheet(stylesheet.replace("__CODEX_FONT__", CODEX_QSS_FONT_FAMILY))

    def _icon_button(self, text: str) -> QPushButton:
        button = QPushButton(text)
        button.setFixedSize(30, 30)
        button.setCursor(Qt.PointingHandCursor)
        stylesheet = """
            QPushButton {
                background-color: transparent;
                border: none;
                border-radius: 15px;
                color: rgba(38, 49, 61, 150);
                font-family: __CODEX_SYMBOL_FONT__;
                font-size: 17px;
                font-weight: 400;
            }

            QPushButton:hover {
                background-color: rgba(255, 255, 255, 125);
                color: #26313D;
            }
            """
        button.setStyleSheet(
            stylesheet.replace("__CODEX_SYMBOL_FONT__", CODEX_SYMBOL_QSS_FONT_FAMILY)
        )
        return button

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.task_id)

        super().mousePressEvent(event)

    def _color_for_category(self, category: DeadlineCategory, completed: bool) -> str:
        if completed:
            return "#5CBFA6"
        if category == DeadlineCategory.OVERDUE:
            return "#E85D5D"
        if category == DeadlineCategory.WITHIN_ONE_HOUR:
            return "#F2994A"
        if category == DeadlineCategory.WITHIN_ONE_DAY:
            return "#D99A2B"
        return "#3B9AB2"
