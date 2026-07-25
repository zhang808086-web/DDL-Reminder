from __future__ import annotations

from PySide6.QtCore import QRectF, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QToolButton


class WindowControlButton(QToolButton):
    def __init__(self, kind: str, parent=None) -> None:
        super().__init__(parent)
        self.kind = kind
        self.setObjectName("closeWindowButton" if kind == "close" else "windowButton")
        self.setCursor(Qt.PointingHandCursor)
        self.setFixedSize(30, 30)
        self.setText("")

    def paintEvent(self, event) -> None:
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)

        color = QColor("#D93636" if self.kind == "close" and self.underMouse() else "#44515F")
        color.setAlpha(220 if self.underMouse() else 185)
        pen = QPen(color, 1.7, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        if self.kind == "minimize":
            painter.drawLine(10, 17, 20, 17)
        elif self.kind == "maximize":
            painter.drawRoundedRect(QRectF(10.5, 10.5, 9.0, 9.0), 1.2, 1.2)
        elif self.kind == "close":
            painter.drawLine(11, 11, 19, 19)
            painter.drawLine(19, 11, 11, 19)
