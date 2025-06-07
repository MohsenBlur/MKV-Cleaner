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
from PySide6.QtCore import QSettings, QTimer


def set_dynamic_modern_style(app: QApplication) -> None:
    """Apply a dark theme with an accent color to ``app``."""
    accents = [
        "#429aff",  # blue
        "#30d0c6",  # teal
        "#ab47bc",  # purple
        "#ffa726",  # orange
        "#6fc3df",  # light blue/teal
        "#ff79c6",  # pink/magenta
    ]
    settings = QSettings("MKVToolsCorp", "MKVCleaner")
    accent = settings.value("accent_color", "")
    if not accent:
        accent = random.choice(accents)

    app.setStyleSheet(
        f"""
        QMainWindow, QWidget {{
            background-color: #181a20;
            color: #d2e0f0;
            font-family: 'Segoe UI', 'Noto Color Emoji';
        }}
        QTableView {{
            background: #22242a;
            alternate-background-color: #252b33;
            color: #d0e8f7;
            gridline-color: #34394c;
            /* highlight rows via borders, not filled background */
            selection-background-color: transparent;
            selection-color: #fff;
            font-family: 'Segoe UI', 'Noto Color Emoji';
            font-size: 16px;
        }}
        QTableView::item {{
            border-right: none;
            border-bottom: 1px solid #34394c;
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
            background-color: #232a34;
            color: #8fdfff;
            border-bottom: 2px solid {accent}88;
            font-weight: bold;
            font-family: 'Segoe UI', 'Noto Color Emoji';
            font-size: 16px;
        }}
        QPushButton {{
            background: #262e36;
            color: #bddcff;
            border-radius: 8px;
            border: 2px solid #344b60;
            padding: 5px 16px;
            font-size: 15px;
            font-family: 'Segoe UI', 'Noto Color Emoji';
        }}
        QPushButton:hover {{
            background: {accent}55;
            color: #fff;
            border: 2px solid {accent};
        }}
        QPushButton:checked, QPushButton:default {{
            background: {accent};
            color: #fff;
            border: 2px solid #39aacc;
        }}
        QLineEdit, QComboBox, QSpinBox {{
            background: #1e232c;
            color: #b5e3ff;
            border-radius: 6px;
            border: 1.5px solid #2d3c4c;
            font-family: 'Segoe UI', 'Noto Color Emoji';
        }}
        QToolTip {{
            background: #2a4154;
            color: #fff;
            border: 1px solid {accent};
            font-family: 'Segoe UI', 'Noto Color Emoji';
        }}
        /* GroupBar specific: */
        #GroupBar QLabel {{
            color: #fff;
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
    splash.show()
    app.processEvents()
    win = MainWindow()
    win.show()
    QTimer.singleShot(1000, lambda: splash.finish(win))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
