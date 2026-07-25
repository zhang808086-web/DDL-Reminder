from __future__ import annotations

from PySide6.QtCore import QPointF, QRectF, Qt, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QAbstractButton,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
)

from ddl_reminder.infrastructure.autostart import (
    WindowsAutostart,
    build_autostart_command,
    is_packaged_app,
)
from ddl_reminder.ui.theme import CODEX_CJK_QSS_FONT_FAMILY, CODEX_QSS_FONT_FAMILY
from ddl_reminder.ui.window_control_button import WindowControlButton


class ToggleSwitch(QAbstractButton):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(54, 30)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        enabled = self.isEnabled()
        checked = self.isChecked()
        track_color = QColor("#2563EB" if checked else "#CBD5E1")
        if not enabled:
            track_color = QColor("#E2E8F0")

        painter.setPen(Qt.NoPen)
        painter.setBrush(track_color)
        painter.drawRoundedRect(QRectF(1, 1, 52, 28), 14, 14)

        knob_x = 27 if checked else 3
        knob_color = QColor("#FFFFFF" if enabled else "#F8FAFC")
        painter.setBrush(knob_color)
        painter.drawEllipse(QPointF(knob_x + 12, 15), 12, 12)


class SettingsDialog(QDialog):
    autostart_changed = Signal(bool)

    def __init__(self, autostart: WindowsAutostart, parent=None) -> None:
        super().__init__(parent)
        self.autostart = autostart
        self.setWindowTitle("设置")
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setModal(True)
        self.resize(380, 220)
        self._setup_ui()

    def _setup_ui(self) -> None:
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(10, 10, 10, 10)
        root_layout.setSpacing(0)

        shell = QFrame()
        shell.setObjectName("settingsShell")
        root_layout.addWidget(shell)

        shell_layout = QVBoxLayout(shell)
        shell_layout.setContentsMargins(22, 22, 22, 22)
        shell_layout.setSpacing(24)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(12)

        title_label = QLabel("设置")
        title_label.setObjectName("dialogTitle")

        close_btn = WindowControlButton("close")
        close_btn.clicked.connect(self.reject)

        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(close_btn)

        option_panel = QFrame()
        option_panel.setObjectName("optionPanel")
        option_layout = QHBoxLayout(option_panel)
        option_layout.setContentsMargins(16, 14, 16, 14)
        option_layout.setSpacing(14)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(6)

        option_title = QLabel("开机自启")
        option_title.setObjectName("optionTitle")

        hint_text = "开机后只显示 DDL 悬浮窗"
        if not is_packaged_app():
            hint_text = "仅打包成 exe 后可启用"

        option_hint = QLabel(hint_text)
        option_hint.setObjectName("optionHint")

        text_layout.addWidget(option_title)
        text_layout.addWidget(option_hint)

        self.autostart_switch = ToggleSwitch()
        self.autostart_switch.setEnabled(is_packaged_app())
        self.autostart_switch.setChecked(
            self.autostart.is_enabled(build_autostart_command())
        )
        self.autostart_switch.toggled.connect(self._toggle_autostart)

        option_layout.addLayout(text_layout, 1)
        option_layout.addWidget(self.autostart_switch)

        shell_layout.addLayout(header_layout)
        shell_layout.addWidget(option_panel)
        shell_layout.addStretch()

        self._apply_styles()

    def _toggle_autostart(self, checked: bool) -> None:
        try:
            if checked:
                self.autostart.enable(build_autostart_command())
            else:
                self.autostart.disable()
        except OSError as error:
            self.autostart_switch.blockSignals(True)
            self.autostart_switch.setChecked(not checked)
            self.autostart_switch.blockSignals(False)
            QMessageBox.warning(self, "设置失败", str(error))
            return

        self.autostart_changed.emit(checked)

    def _apply_styles(self) -> None:
        stylesheet = """
            QDialog {
                background-color: transparent;
                font-family: __CODEX_FONT__;
            }

            QFrame#settingsShell {
                background-color: rgba(246, 250, 255, 232);
                border: 1px solid rgba(255, 255, 255, 210);
                border-radius: 18px;
            }

            QLabel#dialogTitle {
                color: #121A26;
                font-family: __CODEX_CJK_FONT__;
                font-size: 18px;
                font-weight: 600;
            }

            QFrame#optionPanel {
                background-color: rgba(255, 255, 255, 125);
                border: 1px solid rgba(115, 132, 153, 55);
                border-radius: 12px;
            }

            QLabel#optionTitle {
                color: #121A26;
                font-family: __CODEX_CJK_FONT__;
                font-size: 15px;
                font-weight: 500;
            }

            QLabel#optionHint {
                color: rgba(18, 26, 38, 130);
                font-family: __CODEX_CJK_FONT__;
                font-size: 13px;
                font-weight: 400;
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
            stylesheet.replace("__CODEX_FONT__", CODEX_QSS_FONT_FAMILY).replace(
                "__CODEX_CJK_FONT__", CODEX_CJK_QSS_FONT_FAMILY
            )
        )
