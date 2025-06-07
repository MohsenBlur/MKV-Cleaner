"""Application entry point for the MKV Cleaner GUI.

This module starts a :class:`~PySide6.QtWidgets.QApplication`, applies a
randomized modern style and opens the main window. Run the ``mkv-cleaner``
console script or execute this module directly to launch the application.
"""

import sys
import random

from core.bootstrap import ensure_python_package

ensure_python_package("PySide6")
if sys.version_info < (3, 11):
    ensure_python_package("tomli")

from gui.main_window import MainWindow
from gui.widgets.fast_tooltip_style import FastToolTipStyle
from gui.widgets.logo_splash import LogoSplash
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtCore import QSettings, QTimer, QPropertyAnimation, QAbstractAnimation
from gui.theme import COLORS, FONT_SIZES, ACCENT_OPTIONS


def set_dynamic_modern_style(app: QApplication) -> None:
    """Apply a dark theme with an accent color to ``app``."""
    accents = ACCENT_OPTIONS
    settings = QSettings("MKVToolsCorp", "MKVCleaner")
    accent = settings.value("accent_color", "")
    if not accent:
        accent = random.choice(accents)

    app.setStyleSheet(
        f"""
        QMainWindow, QWidget {{
            background-color: {COLORS['bg_main']};
            color: {COLORS['text_main']};
            font-family: 'Segoe UI', 'Noto Color Emoji';
        }}
        QTableView {{
            background: {COLORS['table_bg']};
            alternate-background-color: {COLORS['table_alt_bg']};
            color: {COLORS['table_text']};
            gridline-color: {COLORS['gridline']};
            /* highlight rows via borders, not filled background */
            selection-background-color: transparent;
            selection-color: {COLORS['white']};
            font-family: 'Segoe UI', 'Noto Color Emoji';
            font-size: {FONT_SIZES['default']}px;
        }}
        QTableView::item {{
            border-right: none;
            border-bottom: 1px solid {COLORS['gridline']};
        }}
        QTableView::item:selected {{
            /* highlight row with accent color */
            border-right: none;
            border-left: none;
            border-top: 1px solid {accent};
            border-bottom: 1px solid {accent};
        }}
        QTableView::item:focus {{
            outline: none;
        }}
        QHeaderView::section {{
            background-color: {COLORS['header_bg']};
            color: {COLORS['header_text']};
            border-bottom: 2px solid {accent}88;
            font-weight: bold;
            font-family: 'Segoe UI', 'Noto Color Emoji';
            font-size: {FONT_SIZES['default']}px;
        }}
        QPushButton {{
            background: {COLORS['btn_bg']};
            color: {COLORS['btn_text']};
            border-radius: 8px;
            border: 2px solid {COLORS['btn_border']};
            padding: 5px 16px;
            font-size: {FONT_SIZES['medium']}px;
            font-family: 'Segoe UI', 'Noto Color Emoji';
        }}
        QPushButton:hover {{
            background: {accent}55;
            color: {COLORS['white']};
            border: 2px solid {accent};
        }}
        QPushButton:checked, QPushButton:default {{
            background: {accent};
            color: {COLORS['white']};
            border: 2px solid {COLORS['checked_border']};
        }}
        QLineEdit, QComboBox, QSpinBox {{
            background: {COLORS['input_bg']};
            color: {COLORS['input_text']};
            border-radius: 6px;
            border: 1.5px solid {COLORS['input_border']};
            font-family: 'Segoe UI', 'Noto Color Emoji';
        }}
        QToolTip {{
            background: {COLORS['tooltip_bg']};
            color: {COLORS['white']};
            border: 1px solid {accent};
            font-family: 'Segoe UI', 'Noto Color Emoji';
        }}
        /* GroupBar specific: */
        #GroupBar QLabel {{
            color: {COLORS['white']};
        }}
    """
    )


def main() -> None:
    """Create the application and show the main window."""
    app = QApplication(sys.argv)
    font_path = Path(__file__).resolve().parent / "fonts" / "NotoColorEmoji.ttf"
    if font_path.exists():
        font_id = QFontDatabase.addApplicationFont(str(font_path))
        if font_id != -1:
            noto_family = QFontDatabase.applicationFontFamilies(font_id)[0]
            QFont.insertSubstitution("Segoe UI Emoji", noto_family)
            QFont.insertSubstitution("Segoe UI Symbol", noto_family)
            font_fams = ["Segoe UI", "Segoe UI Emoji", noto_family]
        else:
            font_fams = ["Segoe UI", "Segoe UI Emoji"]
    else:
        font_fams = ["Segoe UI", "Segoe UI Emoji"]
    font = QFont()
    font.setFamilies(font_fams)
    app.setFont(font)
    # Show tooltips faster than the Qt default
    app.setStyle(FastToolTipStyle(app.style()))
    set_dynamic_modern_style(app)
    splash = LogoSplash()
    splash.setWindowOpacity(0.0)
    splash.show()
    app.processEvents()

    center_pos = splash.pos()
    shake_timer = QTimer()
    shake_timer.setInterval(5)

    def _shake():
        splash.move(
            center_pos.x() + random.randint(-3, 3),
            center_pos.y() + random.randint(-3, 3),
        )

    shake_timer.timeout.connect(_shake)

    fade_in_anim = QPropertyAnimation(splash, b"windowOpacity")
    fade_in_anim.setDuration(200)
    fade_in_anim.setStartValue(0.0)
    fade_in_anim.setEndValue(1.0)

    def _finish_fade_in():
        shake_timer.stop()
        splash.move(center_pos)

    fade_in_anim.finished.connect(_finish_fade_in)
    shake_timer.start()
    fade_in_anim.start(QAbstractAnimation.DeleteWhenStopped)

    splash._fade_in_anim = fade_in_anim
    splash._shake_timer = shake_timer
    win = MainWindow()
    win.show()

    def fade_and_finish():
        anim = QPropertyAnimation(splash, b"windowOpacity")
        anim.setDuration(500)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(lambda: splash.finish(win))
        anim.start(QAbstractAnimation.DeleteWhenStopped)
        # keep reference so it doesn't get garbage collected
        splash._fade_anim = anim

    QTimer.singleShot(1000, fade_and_finish)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
