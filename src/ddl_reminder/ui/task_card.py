from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from ddl_reminder.ui.theme import CODEX_QSS_FONT_FAMILY, CODEX_SYMBOL_QSS_FONT_FAMILY


class TaskCard(QFrame):
    clicked = Signal(int)

    def __init__(
        self,
        task_id: int,
        title: str,
        remaining_text: str,
        color: str,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self.task_id = task_id
        self.setFixedHeight(92)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._setup_ui(title, remaining_text, color)

    def _setup_ui(self, title: str, remaining_text: str, color: str) -> None:
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("taskCard")

        root_layout = QHBoxLayout(self)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        color_bar = QWidget()
        color_bar.setObjectName("colorBar")
        color_bar.setFixedWidth(4)
        color_bar.setStyleSheet(
            f"""
            QWidget#colorBar {{
                background-color: {color};
                border-top-left-radius: 12px;
                border-bottom-left-radius: 12px;
            }}
            """
        )
        root_layout.addWidget(color_bar)

        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(18, 14, 16, 14)
        content_layout.setSpacing(12)

        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(0, 0, 0, 0)
        text_layout.setSpacing(8)

        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(10)

        dot = QLabel()
        dot.setObjectName("statusDot")
        dot.setFixedSize(8, 8)
        dot.setStyleSheet(
            f"""
            QLabel#statusDot {{
                background-color: {color};
                border-radius: 4px;
            }}
            """
        )

        title_label = QLabel(title)
        title_label.setObjectName("taskTitle")
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        title_label.setTextInteractionFlags(Qt.NoTextInteraction)

        title_row.addWidget(dot)
        title_row.addWidget(title_label, 1)

        time_label = QLabel(f"◷ {remaining_text}")
        time_label.setObjectName("remainingText")
        time_label.setTextInteractionFlags(Qt.NoTextInteraction)
        time_label.setStyleSheet(
            f"""
            QLabel#remainingText {{
                color: {color};
                font-family: {CODEX_QSS_FONT_FAMILY};
                font-size: 15px;
                font-weight: 600;
            }}
            """
        )

        text_layout.addLayout(title_row)
        text_layout.addWidget(time_label)

        arrow_label = QLabel("›")
        arrow_label.setObjectName("arrowLabel")
        arrow_label.setAlignment(Qt.AlignCenter)
        arrow_label.setFixedWidth(20)

        content_layout.addLayout(text_layout, 1)
        content_layout.addWidget(arrow_label)

        root_layout.addLayout(content_layout, 1)

        stylesheet = """
            QFrame#taskCard {
                background-color: rgba(255, 255, 255, 185);
                border: 1px solid rgba(255, 255, 255, 165);
                border-radius: 12px;
                font-family: __CODEX_FONT__;
            }

            QFrame#taskCard:hover {
                background-color: rgba(255, 255, 255, 220);
            }

            QLabel#taskTitle {
                color: #26313D;
                font-family: __CODEX_FONT__;
                font-size: 16px;
                font-weight: 600;
            }

            QLabel#arrowLabel {
                color: rgba(38, 49, 61, 120);
                font-family: __CODEX_SYMBOL_FONT__;
                font-size: 28px;
                font-weight: 300;
            }
            """
        self.setStyleSheet(
            stylesheet.replace("__CODEX_FONT__", CODEX_QSS_FONT_FAMILY).replace(
                "__CODEX_SYMBOL_FONT__", CODEX_SYMBOL_QSS_FONT_FAMILY
            )
        )

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.task_id)

        super().mousePressEvent(event)
