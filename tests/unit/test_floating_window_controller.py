from PySide6.QtCore import QObject, QPoint, QRect, QSize

from ddl_reminder.ui.floating_window_controller import (
    clamp_position,
    collapsed_position,
    expanded_position,
    nearest_edge,
    FloatingWindowController,
)


SCREEN = QRect(100, 50, 1000, 700)
WINDOW = QSize(300, 430)


def test_clamp_position_moves_saved_offscreen_position_into_available_geometry():
    assert clamp_position(QPoint(-900, 1200), WINDOW, SCREEN) == QPoint(100, 320)


def test_nearest_edge_uses_inclusive_threshold_for_every_screen_edge():
    cases = [
        (QPoint(124, 180), 24, "left"),
        (QPoint(776, 180), 24, "right"),
        (QPoint(300, 74), 24, "top"),
        (QPoint(300, 296), 24, "bottom"),
        (QPoint(125, 180), 24, None),
    ]

    for position, threshold, expected in cases:
        assert nearest_edge(position, WINDOW, SCREEN, threshold) == expected


def test_expanded_position_snaps_to_each_edge_and_clamps_other_axis():
    assert expanded_position("left", QPoint(130, -500), WINDOW, SCREEN) == QPoint(100, 50)
    assert expanded_position("right", QPoint(760, 900), WINDOW, SCREEN) == QPoint(800, 320)
    assert expanded_position("top", QPoint(-500, 70), WINDOW, SCREEN) == QPoint(100, 50)
    assert expanded_position("bottom", QPoint(1200, 280), WINDOW, SCREEN) == QPoint(800, 320)


def test_collapsed_position_keeps_only_requested_strip_visible():
    expanded = QPoint(100, 150)

    assert collapsed_position("left", expanded, WINDOW, SCREEN, 14) == QPoint(-186, 150)
    assert collapsed_position("right", QPoint(800, 150), WINDOW, SCREEN, 14) == QPoint(1086, 150)
    assert collapsed_position("top", QPoint(300, 50), WINDOW, SCREEN, 14) == QPoint(300, -366)
    assert collapsed_position("bottom", QPoint(300, 320), WINDOW, SCREEN, 14) == QPoint(300, 736)


class FakeSettings:
    def __init__(self, position=None):
        self.values = {"floating_window/pos": position}

    def value(self, key):
        return self.values.get(key)

    def setValue(self, key, value):
        self.values[key] = QPoint(value)


class FakeWindow(QObject):
    def __init__(self, position=QPoint(200, 100)):
        super().__init__()
        self._position = QPoint(position)
        self.shown = False
        self.raised = False
        self.activated = False

    def position(self):
        return QPoint(self._position)

    def setPosition(self, position):
        self._position = QPoint(position)

    def width(self):
        return WINDOW.width()

    def height(self):
        return WINDOW.height()

    def show(self):
        self.shown = True

    def raise_(self):
        self.raised = True

    def requestActivate(self):
        self.activated = True


def make_controller(settings=None):
    return FloatingWindowController(
        settings=settings or FakeSettings(),
        screen_geometry_provider=lambda _window: SCREEN,
    )


def test_attach_restores_and_clamps_saved_position():
    settings = FakeSettings(QPoint(-900, 1200))
    window = FakeWindow()

    make_controller(settings).attachWindow(window)

    assert window.position() == QPoint(100, 320)
    assert settings.values["floating_window/pos"] == QPoint(100, 320)


def test_finish_drag_snaps_to_nearby_edge_and_saves_expanded_position():
    settings = FakeSettings()
    window = FakeWindow(QPoint(150, 180))
    controller = make_controller(settings)
    controller.attachWindow(window)
    window.setPosition(QPoint(124, 180))

    controller.beginDrag()
    controller.finishDrag()

    assert window.position() == QPoint(100, 180)
    assert controller.dockSide == "left"
    assert settings.values["floating_window/pos"] == QPoint(100, 180)


def test_pin_expands_a_collapsed_window_and_prevents_collapse():
    window = FakeWindow(QPoint(124, 180))
    controller = make_controller()
    controller.attachWindow(window)
    controller.finishDrag()
    controller.collapse()
    assert controller.collapsed is True

    controller.togglePinned()

    assert controller.pinned is True
    assert controller.collapsed is False
    assert window.position() == QPoint(100, 180)
    controller.collapse()
    assert controller.collapsed is False


def test_show_from_tray_expands_and_activates_window():
    window = FakeWindow(QPoint(124, 180))
    controller = make_controller()
    controller.attachWindow(window)
    controller.finishDrag()
    controller.collapse()

    controller.showFromTray()

    assert controller.collapsed is False
    assert window.position() == QPoint(100, 180)
    assert window.shown is True
    assert window.raised is True
    assert window.activated is True


def test_collapsed_position_is_not_persisted():
    settings = FakeSettings()
    window = FakeWindow(QPoint(124, 180))
    controller = make_controller(settings)
    controller.attachWindow(window)
    controller.finishDrag()
    controller.collapse()

    controller.savePosition()

    assert settings.values["floating_window/pos"] == QPoint(100, 180)
