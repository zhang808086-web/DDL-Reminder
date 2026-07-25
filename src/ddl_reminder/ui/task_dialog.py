from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time
from pathlib import Path

from PySide6.QtCore import QDate, QPoint, Qt, QTime
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QTimeEdit,
    QVBoxLayout,
    QWidget,
)

from ddl_reminder.ui.theme import CODEX_CJK_QSS_FONT_FAMILY, CODEX_QSS_FONT_FAMILY
from ddl_reminder.ui.window_control_button import WindowControlButton


@dataclass
class TaskFormData:
    title: str
    description: str
    deadline_date: date
    deadline_time: time | None


class TaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._drag_offset: QPoint | None = None
        self.setWindowTitle("新建任务")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)
        self.resize(360, 560)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("detailShell")
        root_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(22, 22, 22, 18)
        shell_layout.setSpacing(0)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title_label = QLabel("新建任务")
        title_label.setObjectName("dialogTitle")

        close_btn = WindowControlButton("close")
        close_btn.setToolTip("关闭")
        close_btn.clicked.connect(self.reject)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)

        form_layout = QVBoxLayout()
        form_layout.setContentsMargins(0, 28, 0, 0)
        form_layout.setSpacing(24)

        self.title_edit = QLineEdit()
        self.title_edit.setObjectName("detailInput")
        self.title_edit.setPlaceholderText("输入任务标题")
        form_layout.addWidget(self._field_group("标题", self.title_edit))

        self.description_edit = QTextEdit()
        self.description_edit.setObjectName("detailTextArea")
        self.description_edit.setPlaceholderText("输入任务描述")
        form_layout.addWidget(self._field_group("描述", self.description_edit))

        self.deadline_date_edit = QDateEdit()
        self.deadline_date_edit.setObjectName("detailInput")
        self.deadline_date_edit.setCalendarPopup(True)
        self.deadline_date_edit.setDisplayFormat("M月d日")
        self.deadline_date_edit.setDate(QDate.currentDate())

        self.deadline_time_edit = QTimeEdit()
        self.deadline_time_edit.setObjectName("detailInput")
        self.deadline_time_edit.setDisplayFormat("HH:mm")
        self.deadline_time_edit.setTime(QTime(23, 59))

        ddl_group = QWidget()
        ddl_layout = QVBoxLayout(ddl_group)
        ddl_layout.setContentsMargins(0, 0, 0, 0)
        ddl_layout.setSpacing(10)

        ddl_label = QLabel("DDL")
        ddl_label.setObjectName("fieldLabel")

        ddl_inputs = QHBoxLayout()
        ddl_inputs.setContentsMargins(0, 0, 0, 0)
        ddl_inputs.setSpacing(10)
        ddl_inputs.addWidget(self.deadline_date_edit)
        ddl_inputs.addWidget(self.deadline_time_edit)

        ddl_layout.addWidget(ddl_label)
        ddl_layout.addLayout(ddl_inputs)
        form_layout.addWidget(ddl_group)
        form_layout.addStretch()

        footer = QFrame()
        footer.setObjectName("detailFooter")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(0, 16, 0, 0)
        footer_layout.setSpacing(12)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setObjectName("secondaryButton")
        self.cancel_btn.clicked.connect(self.reject)

        self.create_btn = QPushButton("创建")
        self.create_btn.setObjectName("primaryButton")
        self.create_btn.clicked.connect(self.accept)

        footer_layout.addStretch()
        footer_layout.addWidget(self.cancel_btn)
        footer_layout.addWidget(self.create_btn)

        shell_layout.addLayout(header_layout)
        shell_layout.addLayout(form_layout, 1)
        shell_layout.addWidget(footer)

        self._apply_styles()

    def _field_group(self, label_text: str, field: QWidget) -> QWidget:
        group = QWidget()
        layout = QVBoxLayout(group)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        label = QLabel(label_text)
        label.setObjectName("fieldLabel")

        layout.addWidget(label)
        layout.addWidget(field)
        return group

    def _apply_styles(self) -> None:
        stylesheet = """
            QDialog {
                background-color: transparent;
                font-family: __CODEX_FONT__;
            }

            QFrame#detailShell {
                background-color: rgba(246, 250, 255, 226);
                border: 1px solid rgba(255, 255, 255, 210);
                border-radius: 18px;
            }

            QLabel#dialogTitle {
                color: #121A26;
                font-family: __CODEX_CJK_FONT__;
                font-size: 18px;
                font-weight: 600;
            }

            QLabel#fieldLabel {
                color: rgba(18, 26, 38, 215);
                font-family: __CODEX_CJK_FONT__;
                font-size: 14px;
                font-weight: 500;
            }

            QLineEdit#detailInput,
            QDateEdit#detailInput,
            QTimeEdit#detailInput,
            QTextEdit#detailTextArea {
                background-color: rgba(255, 255, 255, 165);
                border: 1px solid rgba(115, 132, 153, 78);
                border-radius: 7px;
                color: #121A26;
                font-family: __CODEX_CJK_FONT__;
                font-size: 14px;
                font-weight: 400;
                selection-background-color: rgba(37, 99, 235, 80);
            }

            QLineEdit#detailInput,
            QDateEdit#detailInput,
            QTimeEdit#detailInput {
                min-height: 38px;
                padding: 0 12px;
            }

            QLineEdit#detailInput::placeholder,
            QTextEdit#detailTextArea::placeholder {
                color: rgba(18, 26, 38, 95);
            }

            QDateEdit#detailInput {
                padding-right: 32px;
            }

            QDateEdit#detailInput::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 30px;
                border: none;
                border-left: 1px solid rgba(115, 132, 153, 55);
                border-top-right-radius: 7px;
                border-bottom-right-radius: 7px;
                background-color: transparent;
            }

            QDateEdit#detailInput::down-arrow {
                image: url("__CHEVRON_DOWN__");
                width: 10px;
                height: 10px;
            }

            QTimeEdit#detailInput {
                padding-right: 52px;
            }

            QTimeEdit#detailInput::up-button,
            QTimeEdit#detailInput::down-button {
                subcontrol-origin: border;
                width: 26px;
                border-left: 1px solid rgba(115, 132, 153, 55);
                background-color: transparent;
            }

            QTimeEdit#detailInput::up-button {
                subcontrol-position: top right;
                border-bottom: 1px solid rgba(115, 132, 153, 35);
                border-top-right-radius: 7px;
            }

            QTimeEdit#detailInput::down-button {
                subcontrol-position: bottom right;
                border-bottom-right-radius: 7px;
            }

            QTimeEdit#detailInput::up-arrow {
                image: url("__CHEVRON_UP__");
                width: 10px;
                height: 10px;
            }

            QTimeEdit#detailInput::down-arrow {
                image: url("__CHEVRON_DOWN__");
                width: 10px;
                height: 10px;
            }

            QTextEdit#detailTextArea {
                min-height: 118px;
                padding: 10px 12px;
            }

            QLineEdit#detailInput:focus,
            QDateEdit#detailInput:focus,
            QTimeEdit#detailInput:focus,
            QTextEdit#detailTextArea:focus {
                border-color: rgba(37, 99, 235, 140);
                background-color: rgba(255, 255, 255, 195);
            }

            QFrame#detailFooter {
                border-top: 1px solid rgba(115, 132, 153, 42);
                background-color: transparent;
            }

            QPushButton#primaryButton,
            QPushButton#secondaryButton {
                min-width: 82px;
                min-height: 38px;
                border-radius: 7px;
                font-family: __CODEX_CJK_FONT__;
                font-size: 14px;
                font-weight: 500;
            }

            QPushButton#primaryButton {
                background-color: #2563EB;
                border: 1px solid rgba(255, 255, 255, 120);
                color: white;
            }

            QPushButton#primaryButton:hover {
                background-color: #1D4ED8;
            }

            QPushButton#secondaryButton {
                background-color: rgba(255, 255, 255, 140);
                border: 1px solid rgba(115, 132, 153, 70);
                color: #121A26;
            }

            QPushButton#secondaryButton:hover {
                background-color: rgba(255, 255, 255, 205);
                border-color: rgba(115, 132, 153, 110);
            }

            QToolButton#closeWindowButton {
                background-color: rgba(255, 255, 255, 58);
                border: 1px solid rgba(74, 86, 101, 80);
                border-radius: 8px;
            }

            QToolButton#closeWindowButton:hover {
                background-color: rgba(232, 93, 93, 35);
                border-color: rgba(232, 93, 93, 150);
            }
        """
        assets_dir = Path(__file__).resolve().parent / "assets"
        chevron_down = (assets_dir / "chevron_down.svg").as_posix()
        chevron_up = (assets_dir / "chevron_up.svg").as_posix()
        self.setStyleSheet(
            stylesheet.replace("__CODEX_FONT__", CODEX_QSS_FONT_FAMILY).replace(
                "__CODEX_CJK_FONT__", CODEX_CJK_QSS_FONT_FAMILY
            ).replace(
                "__CHEVRON_DOWN__", chevron_down
            ).replace(
                "__CHEVRON_UP__", chevron_up
            )
        )

    def get_data(self) -> TaskFormData:
        qdate = self.deadline_date_edit.date()
        qtime = self.deadline_time_edit.time()

        return TaskFormData(
            title=self.title_edit.text(),
            description=self.description_edit.toPlainText(),
            deadline_date=date(qdate.year(), qdate.month(), qdate.day()),
            deadline_time=time(qtime.hour(), qtime.minute(), qtime.second()),
        )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton and event.position().y() <= 86:
            self._drag_offset = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()
            return

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_offset)
            event.accept()
            return

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_offset = None
        super().mouseReleaseEvent(event)
