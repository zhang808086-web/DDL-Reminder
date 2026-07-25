from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import (
    QEasingCurve,
    QDateTime,
    QPoint,
    QPropertyAnimation,
    QSettings,
    Signal,
    Qt,
    QTimer,
)
from PySide6.QtGui import QColor, QCursor
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ddl_reminder.domain.deadline import (
    DeadlineCategory,
    classify_deadline,
    format_remaining_time,
)
from ddl_reminder.domain.exceptions import TaskError
from ddl_reminder.ui.task_card import TaskCard
from ddl_reminder.ui.task_detail_dialog import TaskDetailDialog
from ddl_reminder.ui.theme import CODEX_QSS_FONT_FAMILY, CODEX_SYMBOL_QSS_FONT_FAMILY


class FloatingWindow(QWidget):
    """Desktop floating window showing the most urgent DDL tasks."""

    tasks_changed = Signal()

    def __init__(self, task_service, parent=None):
        super().__init__(parent)
        self.task_service = task_service
        self.settings = QSettings("ddl-reminder", "ddl-reminder")
        self._allow_close = False
        self._pinned = False
        self._drag_offset: QPoint | None = None
        self._dock_side: str | None = None
        self._is_collapsed = False
        self._collapsed_visible_size = 14
        self._dock_threshold = 24
        self._snap_threshold = 80
        self._edge_animation_running = False
        self._ignore_collapse_until_ms = 0

        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setDuration(180)
        self._animation.setEasingCurve(QEasingCurve.OutCubic)
        self._animation.finished.connect(self._finish_edge_animation)

        self._setup_ui()
        self._restore_position()
        self._setup_timer()
        self.refresh_tasks()

    def _setup_ui(self) -> None:
        self.setWindowTitle("DDL")
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.resize(300, 430)

        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(8, 8, 8, 8)
        root_layout.setSpacing(0)

        self.panel = QFrame()
        self.panel.setObjectName("glassPanel")
        self._refresh_panel_style()

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(32)
        shadow.setOffset(0, 10)
        shadow.setColor(QColor(20, 32, 44, 70))
        self.panel.setGraphicsEffect(shadow)

        root_layout.addWidget(self.panel)

        panel_layout = QVBoxLayout(self.panel)
        panel_layout.setContentsMargins(22, 22, 22, 22)
        panel_layout.setSpacing(18)

        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(8)

        self.title_label = QLabel("DDL")
        self.title_label.setObjectName("floatingTitle")

        self.pin_button = self._create_header_button("◇")
        self.pin_button.setToolTip("固定悬浮窗，禁止自动收起")
        self.pin_button.clicked.connect(self._toggle_pinned)

        self.close_button = self._create_header_button("×")
        self.close_button.setToolTip("隐藏悬浮窗")
        self.close_button.clicked.connect(self.hide)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.pin_button)
        header_layout.addWidget(self.close_button)
        panel_layout.addLayout(header_layout)

        self.task_cards_layout = QVBoxLayout()
        self.task_cards_layout.setContentsMargins(0, 18, 0, 0)
        self.task_cards_layout.setSpacing(16)
        panel_layout.addLayout(self.task_cards_layout)
        panel_layout.addStretch()

        stylesheet = """
            QLabel#floatingTitle {
                color: #3B4652;
                font-family: __CODEX_FONT__;
                font-size: 15px;
                font-weight: 600;
            }

            QToolButton#headerButton {
                background-color: transparent;
                border: none;
                border-radius: 14px;
                color: rgba(31, 41, 51, 170);
                font-family: __CODEX_SYMBOL_FONT__;
                font-size: 22px;
                font-weight: 300;
            }

            QToolButton#headerButton:hover {
                background-color: rgba(255, 255, 255, 90);
                color: rgba(31, 41, 51, 230);
            }

            QLabel#emptyTasks {
                color: rgba(31, 41, 51, 145);
                font-family: __CODEX_FONT__;
                font-size: 14px;
                font-weight: 500;
            }
            """
        self.setStyleSheet(
            stylesheet.replace("__CODEX_FONT__", CODEX_QSS_FONT_FAMILY).replace(
                "__CODEX_SYMBOL_FONT__", CODEX_SYMBOL_QSS_FONT_FAMILY
            )
        )

    def _create_header_button(self, text: str) -> QToolButton:
        button = QToolButton()
        button.setObjectName("headerButton")
        button.setText(text)
        button.setFixedSize(30, 30)
        button.setCursor(Qt.PointingHandCursor)
        return button

    def _setup_timer(self) -> None:
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_tasks)
        self.timer.start(60_000)

    def refresh_tasks(self) -> None:
        self._clear_task_cards()

        tasks = self.task_service.get_urgent_tasks(limit=3)
        now = datetime.now()

        if not tasks:
            empty_label = QLabel("暂无未完成任务")
            empty_label.setObjectName("emptyTasks")
            empty_label.setAlignment(Qt.AlignCenter)
            self.task_cards_layout.addWidget(empty_label)
            return

        for task in tasks:
            category, _seconds_diff = classify_deadline(task.deadline, now)
            color = self._color_for_category(category)
            remaining_text = format_remaining_time(task.deadline, now)

            card = TaskCard(
                task_id=task.id,
                title=task.title,
                remaining_text=remaining_text,
                color=color,
            )
            card.clicked.connect(self._open_task_detail_by_id)
            self.task_cards_layout.addWidget(card)

    def show_from_tray(self) -> None:
        self.show()
        if self._is_collapsed:
            self._expand_from_edge()
        self.raise_()
        self.activateWindow()

    def _open_task_detail_by_id(self, task_id: int) -> None:
        if task_id is None:
            return

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

            self.refresh_tasks()
            self.tasks_changed.emit()
            return

    def closeEvent(self, event) -> None:
        self._save_position()
        if self._allow_close:
            super().closeEvent(event)
            return

        event.ignore()
        self.hide()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            if self._is_collapsed:
                self._expand_from_edge()
            self._drag_offset = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._drag_offset is not None and event.buttons() & Qt.LeftButton:
            self._animation.stop()
            self._is_collapsed = False
            self._refresh_panel_style()
            self.move(event.globalPosition().toPoint() - self._drag_offset)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event) -> None:
        self._drag_offset = None
        self._snap_to_edge_if_needed()
        super().mouseReleaseEvent(event)

    def moveEvent(self, event) -> None:
        self._save_position()
        if not self._is_collapsed:
            self._update_dock_side()
        super().moveEvent(event)

    def enterEvent(self, event) -> None:
        if self._is_collapsed and not self._edge_animation_running:
            self._expand_from_edge()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if self._should_auto_collapse() and self._collapse_cooldown_has_finished():
            self._collapse_to_edge()
        super().leaveEvent(event)

    def _toggle_pinned(self) -> None:
        self._pinned = not self._pinned
        self.pin_button.setText("◆" if self._pinned else "◇")
        self.pin_button.setToolTip(
            "取消固定，允许自动收起" if self._pinned else "固定悬浮窗，禁止自动收起"
        )

        if self._pinned and self._is_collapsed:
            self._expand_from_edge()

    def _should_auto_collapse(self) -> bool:
        return (
            not self._pinned
            and not self._is_collapsed
            and not self._edge_animation_running
            and self._dock_side is not None
            and self._drag_offset is None
        )

    def _screen_geometry(self):
        screen = QApplication.screenAt(self.frameGeometry().center())
        if screen is None:
            screen = QApplication.primaryScreen()
        if screen is None:
            return None
        return screen.availableGeometry()

    def _update_dock_side(self) -> None:
        self._dock_side = self._nearest_edge_within_threshold(self._dock_threshold)

    def _snap_to_edge_if_needed(self) -> None:
        side = self._nearest_edge_within_threshold(self._snap_threshold)

        if side is None:
            self._dock_side = None
            return

        self._dock_side = side
        target_pos = self._expanded_pos()
        if target_pos is None:
            return

        self._animate_to(target_pos)
        QTimer.singleShot(260, self._collapse_if_cursor_outside)

    def _nearest_edge_within_threshold(self, threshold: int) -> str | None:
        geometry = self._screen_geometry()
        if geometry is None:
            return None

        distances = {
            "left": abs(self.x() - geometry.left()),
            "right": abs((self.x() + self.width()) - geometry.right()),
            "top": abs(self.y() - geometry.top()),
            "bottom": abs((self.y() + self.height()) - geometry.bottom()),
        }
        side, distance = min(distances.items(), key=lambda item: item[1])

        if distance <= threshold:
            return side

        return None

    def _collapse_if_cursor_outside(self) -> None:
        if self.geometry().contains(QCursor.pos()):
            return
        if self._should_auto_collapse():
            self._collapse_to_edge()

    def _collapsed_pos(self) -> QPoint | None:
        if self._dock_side is None:
            return None

        geometry = self._screen_geometry()
        if geometry is None:
            return None

        if self._dock_side == "left":
            return QPoint(
                geometry.left() - self.width() + self._collapsed_visible_size,
                self.y(),
            )
        if self._dock_side == "right":
            return QPoint(
                geometry.right() + 1 - self._collapsed_visible_size,
                self.y(),
            )
        if self._dock_side == "top":
            return QPoint(
                self.x(),
                geometry.top() - self.height() + self._collapsed_visible_size,
            )
        if self._dock_side == "bottom":
            return QPoint(
                self.x(),
                geometry.bottom() + 1 - self._collapsed_visible_size,
            )

        return None

    def _expanded_pos(self) -> QPoint | None:
        if self._dock_side is None:
            return None

        geometry = self._screen_geometry()
        if geometry is None:
            return None

        if self._dock_side == "left":
            return QPoint(geometry.left(), self.y())
        if self._dock_side == "right":
            return QPoint(geometry.right() + 1 - self.width(), self.y())
        if self._dock_side == "top":
            return QPoint(self.x(), geometry.top())
        if self._dock_side == "bottom":
            return QPoint(self.x(), geometry.bottom() + 1 - self.height())

        return None

    def _animate_to(self, target_pos: QPoint) -> None:
        self._animation.stop()
        self._edge_animation_running = True
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(target_pos)
        self._animation.start()

    def _finish_edge_animation(self) -> None:
        self._edge_animation_running = False

    def _collapse_to_edge(self) -> None:
        target_pos = self._collapsed_pos()
        if target_pos is None:
            return

        self._is_collapsed = True
        self._refresh_panel_style()
        self._animate_to(target_pos)

    def _expand_from_edge(self) -> None:
        target_pos = self._expanded_pos()
        if target_pos is None:
            return

        self._is_collapsed = False
        self._refresh_panel_style()
        self._ignore_collapse_until_ms = QDateTime.currentMSecsSinceEpoch() + 450
        self._animate_to(target_pos)

    def _collapse_cooldown_has_finished(self) -> bool:
        return QDateTime.currentMSecsSinceEpoch() >= self._ignore_collapse_until_ms

    def _refresh_panel_style(self) -> None:
        background_alpha = 170 if self._is_collapsed else 125
        border_alpha = 220 if self._is_collapsed else 170
        shadow_blur = 18 if self._is_collapsed else 32

        self.panel.setStyleSheet(
            f"""
            QFrame#glassPanel {{
                background-color: rgba(235, 244, 250, {background_alpha});
                border: 1px solid rgba(255, 255, 255, {border_alpha});
                border-radius: 28px;
            }}
            """
        )

        effect = self.panel.graphicsEffect()
        if isinstance(effect, QGraphicsDropShadowEffect):
            effect.setBlurRadius(shadow_blur)

    def _save_position(self) -> None:
        if not self._is_collapsed:
            self.settings.setValue("floating_window/pos", self.pos())

    def _restore_position(self) -> None:
        pos = self.settings.value("floating_window/pos")

        if pos is not None:
            self.move(pos)

    def allow_close(self) -> None:
        self._allow_close = True

    def _clear_task_cards(self) -> None:
        while self.task_cards_layout.count():
            item = self.task_cards_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _color_for_category(self, category: DeadlineCategory) -> str:
        if category == DeadlineCategory.OVERDUE:
            return "#E85D5D"
        if category == DeadlineCategory.WITHIN_ONE_HOUR:
            return "#F2994A"
        if category == DeadlineCategory.WITHIN_ONE_DAY:
            return "#D99A2B"
        return "#3B9AB2"
