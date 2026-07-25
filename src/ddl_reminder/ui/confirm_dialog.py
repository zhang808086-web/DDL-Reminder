from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ddl_reminder.ui.theme import CODEX_CJK_QSS_FONT_FAMILY, CODEX_QSS_FONT_FAMILY
from ddl_reminder.ui.window_control_button import WindowControlButton


@dataclass(frozen=True)
class ConfirmDialogConfig:
    title: str
    message: str
    hint: str
    confirm_text: str
    color: str
    hover_color: str
    icon_name: str
    icon_background: str
    icon_border: str


CONFIRM_CONFIGS = {
    "restore": ConfirmDialogConfig(
        title="恢复任务",
        message="确定要恢复这个任务吗？",
        hint="恢复后会重新回到进行中。",
        confirm_text="恢复",
        color="#2563EB",
        hover_color="#1D4ED8",
        icon_name="restore.svg",
        icon_background="rgba(37, 99, 235, 24)",
        icon_border="rgba(37, 99, 235, 80)",
    ),
    "delete": ConfirmDialogConfig(
        title="删除任务",
        message="确定要删除这个任务吗？",
        hint="删除后无法恢复。",
        confirm_text="删除",
        color="#EF4444",
        hover_color="#D92121",
        icon_name="trash.svg",
        icon_background="rgba(239, 68, 68, 24)",
        icon_border="rgba(239, 68, 68, 80)",
    ),
    "save": ConfirmDialogConfig(
        title="保存修改",
        message="确定要保存对任务的修改吗？",
        hint="保存后任务信息会立即更新。",
        confirm_text="保存",
        color="#2563EB",
        hover_color="#1D4ED8",
        icon_name="save.svg",
        icon_background="rgba(37, 99, 235, 24)",
        icon_border="rgba(37, 99, 235, 80)",
    ),
}


class ConfirmDialog(QDialog):
    def __init__(self, kind: str, parent=None) -> None:
        super().__init__(parent)
        self.config = CONFIRM_CONFIGS[kind]
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)
        self.resize(420, 250)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("confirmShell")
        root_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(22, 22, 22, 20)
        shell_layout.setSpacing(22)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title_label = QLabel(self.config.title)
        title_label.setObjectName("confirmTitle")

        close_btn = WindowControlButton("close")
        close_btn.setToolTip("关闭")
        close_btn.clicked.connect(self.reject)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)

        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(22)

        icon_box = QFrame()
        icon_box.setObjectName("iconBox")
        icon_box.setFixedSize(58, 58)

        icon_layout = QVBoxLayout(icon_box)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        icon_layout.setSpacing(0)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setPixmap(self._icon().pixmap(30, 30))
        icon_layout.addWidget(icon_label)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 5, 0, 0)
        text_layout.setSpacing(8)

        message_label = QLabel(self.config.message)
        message_label.setObjectName("confirmMessage")

        hint_label = QLabel(self.config.hint)
        hint_label.setObjectName("confirmHint")

        text_layout.addWidget(message_label)
        text_layout.addWidget(hint_label)
        text_layout.addStretch()

        body_layout.addWidget(icon_box)
        body_layout.addLayout(text_layout, 1)

        footer_layout = QHBoxLayout()
        footer_layout.setContentsMargins(0, 0, 0, 0)
        footer_layout.setSpacing(12)

        cancel_btn = QPushButton("取消")
        cancel_btn.setObjectName("cancelButton")
        cancel_btn.clicked.connect(self.reject)

        confirm_btn = QPushButton(self.config.confirm_text)
        confirm_btn.setObjectName("confirmButton")
        confirm_btn.clicked.connect(self.accept)

        footer_layout.addStretch()
        footer_layout.addWidget(cancel_btn)
        footer_layout.addWidget(confirm_btn)

        shell_layout.addLayout(header_layout)
        shell_layout.addLayout(body_layout, 1)
        shell_layout.addLayout(footer_layout)

        self._apply_styles()

    def _icon(self) -> QIcon:
        assets_dir = Path(__file__).resolve().parent / "assets"
        return QIcon(str(assets_dir / self.config.icon_name))

    def _apply_styles(self) -> None:
        stylesheet = """
            QDialog {
                background-color: transparent;
                font-family: __CODEX_FONT__;
            }

            QFrame#confirmShell {
                background-color: rgba(246, 250, 255, 232);
                border: 1px solid rgba(255, 255, 255, 210);
                border-radius: 16px;
            }

            QLabel#confirmTitle {
                color: #121A26;
                font-family: __CODEX_CJK_FONT__;
                font-size: 17px;
                font-weight: 600;
            }

            QFrame#iconBox {
                background-color: __ICON_BACKGROUND__;
                border: 1px solid __ICON_BORDER__;
                border-radius: 29px;
            }

            QLabel#confirmMessage {
                color: #121A26;
                font-family: __CODEX_CJK_FONT__;
                font-size: 16px;
                font-weight: 500;
            }

            QLabel#confirmHint {
                color: rgba(18, 26, 38, 135);
                font-family: __CODEX_CJK_FONT__;
                font-size: 13px;
                font-weight: 400;
            }

            QPushButton#cancelButton,
            QPushButton#confirmButton {
                min-width: 82px;
                min-height: 38px;
                border-radius: 7px;
                font-family: __CODEX_CJK_FONT__;
                font-size: 14px;
                font-weight: 500;
            }

            QPushButton#cancelButton {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid rgba(115, 132, 153, 70);
                color: #121A26;
            }

            QPushButton#cancelButton:hover {
                background-color: rgba(255, 255, 255, 210);
                border-color: rgba(115, 132, 153, 110);
            }

            QPushButton#confirmButton {
                background-color: __CONFIRM_COLOR__;
                border: 1px solid rgba(255, 255, 255, 105);
                color: white;
            }

            QPushButton#confirmButton:hover {
                background-color: __CONFIRM_HOVER__;
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
        self.setStyleSheet(
            stylesheet.replace("__CODEX_FONT__", CODEX_QSS_FONT_FAMILY)
            .replace("__CODEX_CJK_FONT__", CODEX_CJK_QSS_FONT_FAMILY)
            .replace("__CONFIRM_COLOR__", self.config.color)
            .replace("__CONFIRM_HOVER__", self.config.hover_color)
            .replace("__ICON_BACKGROUND__", self.config.icon_background)
            .replace("__ICON_BORDER__", self.config.icon_border)
        )


def ask_confirm(kind: str, parent=None) -> bool:
    return ConfirmDialog(kind, parent).exec() == QDialog.Accepted
