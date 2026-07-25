from __future__ import annotations

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication


CODEX_FONT_FAMILIES = (
    "Inter",
    "Segoe UI Variable Text",
    "Segoe UI Variable",
    "Segoe UI",
    "Microsoft YaHei UI",
    "Microsoft YaHei",
)

CODEX_QSS_FONT_FAMILY = (
    '"Inter", "Segoe UI Variable Text", "Segoe UI Variable", '
    '"Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei", sans-serif'
)

CODEX_CJK_QSS_FONT_FAMILY = (
    '"Microsoft YaHei UI", "Microsoft YaHei", "Segoe UI Variable Text", '
    '"Segoe UI Variable", "Segoe UI", "Inter", sans-serif'
)

CODEX_SYMBOL_QSS_FONT_FAMILY = (
    '"Segoe UI Symbol", "Inter", "Segoe UI Variable Text", '
    '"Segoe UI Variable", "Segoe UI", "Microsoft YaHei UI", "Microsoft YaHei", sans-serif'
)


def preferred_codex_font() -> QFont:
    installed_families = set(QFontDatabase.families())
    family = next(
        (candidate for candidate in CODEX_FONT_FAMILIES if candidate in installed_families),
        "Segoe UI",
    )

    font = QFont(family)
    font.setPointSize(10)
    font.setWeight(QFont.Normal)
    return font


def apply_codex_font(app: QApplication) -> None:
    app.setFont(preferred_codex_font())
