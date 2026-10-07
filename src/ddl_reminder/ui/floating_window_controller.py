from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from PySide6.QtCore import (
    QDateTime,
    QEvent,
    QObject,
    QPoint,
    Property,
    QRect,
    QSettings,
    QSize,
    Signal,
    Slot,
)
from PySide6.QtGui import QGuiApplication


DockSide = Literal["left", "right", "top", "bottom"]


def clamp_position(position: QPoint, window_size: QSize, screen: QRect) -> QPoint:
    """Keep a window's top-left point inside the available screen geometry."""
    max_x = screen.right() + 1 - window_size.width()
    max_y = screen.bottom() + 1 - window_size.height()
    return QPoint(
        min(max(position.x(), screen.left()), max_x),
        min(max(position.y(), screen.top()), max_y),
    )


def nearest_edge(
    position: QPoint,
    window_size: QSize,
    screen: QRect,
    threshold: int,
) -> DockSide | None:
    distances: dict[DockSide, int] = {
        "left": abs(position.x() - screen.left()),
        "right": abs(position.x() + window_size.width() - screen.right()),
        "top": abs(position.y() - screen.top()),
        "bottom": abs(position.y() + window_size.height() - screen.bottom()),
    }
    side, distance = min(distances.items(), key=lambda item: item[1])
    return side if distance <= threshold else None


def expanded_position(
    side: DockSide,
    position: QPoint,
    window_size: QSize,
    screen: QRect,
) -> QPoint:
    clamped = clamp_position(position, window_size, screen)
    if side == "left":
        clamped.setX(screen.left())
    elif side == "right":
        clamped.setX(screen.right() + 1 - window_size.width())
    elif side == "top":
        clamped.setY(screen.top())
    else:
        clamped.setY(screen.bottom() + 1 - window_size.height())
    return clamped


def collapsed_position(
    side: DockSide,
    expanded: QPoint,
    window_size: QSize,
    screen: QRect,
    visible_strip: int,
) -> QPoint:
    collapsed = QPoint(expanded)
    if side == "left":
        collapsed.setX(screen.left() - window_size.width() + visible_strip)
    elif side == "right":
        collapsed.setX(screen.right() + 1 - visible_strip)
    elif side == "top":
        collapsed.setY(screen.top() - window_size.height() + visible_strip)
    else:
        collapsed.setY(screen.bottom() + 1 - visible_strip)
    return collapsed


class FloatingWindowController(QObject):
    pinnedChanged = Signal()
    collapsedChanged = Signal()
    dockSideChanged = Signal()

    def __init__(
        self,
        settings=None,
        screen_geometry_provider: Callable[[QObject], QRect | None] | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._settings = settings or QSettings("ddl-reminder", "ddl-reminder")
        self._screen_geometry_provider = (
            screen_geometry_provider or self._default_screen_geometry
        )
        self._window: QObject | None = None
        self._pinned = False
        self._collapsed = False
        self._dock_side: DockSide | None = None
        self._dragging = False
        self._allow_close = False
        self._ignore_collapse_until_ms = 0
        self._visible_strip = 14
        self._dock_threshold = 24
        self._snap_threshold = 80

    @Property(bool, notify=pinnedChanged)
    def pinned(self) -> bool:
        return self._pinned

    @Property(bool, notify=collapsedChanged)
    def collapsed(self) -> bool:
        return self._collapsed

    @Property(str, notify=dockSideChanged)
    def dockSide(self) -> str:
        return self._dock_side or ""

    @Slot(QObject)
    def attachWindow(self, window: QObject) -> None:
        if self._window is not None:
            self._window.removeEventFilter(self)
        self._window = window
        window.installEventFilter(self)
        self.restorePosition()

    @Slot()
    def togglePinned(self) -> None:
        self._pinned = not self._pinned
        self.pinnedChanged.emit()
        if self._pinned and self._collapsed:
            self._expand()

    @Slot()
    def showFromTray(self) -> None:
        if self._window is None:
            return
        self._window.show()
        if self._collapsed:
            self._expand()
        self._window.raise_()
        self._window.requestActivate()

    @Slot()
    def savePosition(self) -> None:
        if self._window is None or self._collapsed:
            return
        self._settings.setValue("floating_window/pos", self._window.position())

    @Slot()
    def restorePosition(self) -> None:
        if self._window is None:
            return
        screen = self._screen_geometry()
        if screen is None:
            return
        stored = self._settings.value("floating_window/pos")
        position = QPoint(stored) if stored is not None else self._window.position()
        restored = clamp_position(position, self._window_size(), screen)
        self._window.setPosition(restored)
        if stored is not None and restored != position:
            self.savePosition()
        self._update_dock_side(self._dock_threshold)

    @Slot()
    def beginDrag(self) -> None:
        self._dragging = True
        if self._collapsed:
            self._expand()

    @Slot()
    def finishDrag(self) -> None:
        self._dragging = False
        if self._window is None:
            return
        side = self._nearest_edge(self._snap_threshold)
        self._set_dock_side(side)
        if side is not None:
            screen = self._screen_geometry()
            if screen is not None:
                self._window.setPosition(
                    expanded_position(
                        side, self._window.position(), self._window_size(), screen
                    )
                )
        self.savePosition()

    @Slot()
    def collapse(self) -> None:
        if self._pinned or self._collapsed or self._dock_side is None:
            return
        if self._window is None:
            return
        screen = self._screen_geometry()
        if screen is None:
            return
        self._window.setPosition(
            collapsed_position(
                self._dock_side,
                self._window.position(),
                self._window_size(),
                screen,
                self._visible_strip,
            )
        )
        self._collapsed = True
        self.collapsedChanged.emit()

    @Slot()
    def hideWindow(self) -> None:
        if self._window is not None:
            self.savePosition()
            self._window.hide()

    def allowClose(self) -> None:
        self._allow_close = True

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is not self._window:
            return False
        if event.type() == QEvent.Type.Enter and self._collapsed:
            self._expand()
        elif event.type() == QEvent.Type.Leave:
            if (
                not self._dragging
                and QDateTime.currentMSecsSinceEpoch()
                >= self._ignore_collapse_until_ms
            ):
                self.collapse()
        elif event.type() == QEvent.Type.Move and not self._collapsed:
            self._update_dock_side(self._dock_threshold)
            self.savePosition()
        elif event.type() == QEvent.Type.Close:
            self.savePosition()
            if not self._allow_close:
                event.ignore()
                self._window.hide()
                return True
        return False

    def _expand(self) -> None:
        if self._window is None or self._dock_side is None:
            return
        screen = self._screen_geometry()
        if screen is None:
            return
        self._window.setPosition(
            expanded_position(
                self._dock_side,
                self._window.position(),
                self._window_size(),
                screen,
            )
        )
        self._collapsed = False
        self._ignore_collapse_until_ms = QDateTime.currentMSecsSinceEpoch() + 450
        self.collapsedChanged.emit()
        self.savePosition()

    def _window_size(self) -> QSize:
        return QSize(self._window.width(), self._window.height())

    def _nearest_edge(self, threshold: int) -> DockSide | None:
        if self._window is None:
            return None
        screen = self._screen_geometry()
        if screen is None:
            return None
        return nearest_edge(
            self._window.position(), self._window_size(), screen, threshold
        )

    def _update_dock_side(self, threshold: int) -> None:
        self._set_dock_side(self._nearest_edge(threshold))

    def _set_dock_side(self, side: DockSide | None) -> None:
        if self._dock_side == side:
            return
        self._dock_side = side
        self.dockSideChanged.emit()

    def _screen_geometry(self) -> QRect | None:
        if self._window is None:
            return None
        return self._screen_geometry_provider(self._window)

    @staticmethod
    def _default_screen_geometry(window: QObject) -> QRect | None:
        size = QSize(window.width(), window.height())
        center = window.position() + QPoint(size.width() // 2, size.height() // 2)
        screen = QGuiApplication.screenAt(center) or QGuiApplication.primaryScreen()
        return screen.availableGeometry() if screen is not None else None
