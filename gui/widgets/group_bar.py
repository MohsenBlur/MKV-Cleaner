from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
    QSizePolicy,
    QComboBox,
)
from PySide6.QtCore import Qt, QSize, Signal
from core.config import DEFAULTS


class GroupBar(QWidget):
    preferencesClicked = Signal()
    backendChanged = Signal(str)
    prevClicked = Signal()
    nextClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.group_buttons = []
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self._setup_ui()

    def _setup_ui(self):
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(16, 4, 16, 4)
        self.layout.setSpacing(14)

        self.group_label = QLabel("Groups")
        self.group_label.setStyleSheet(
            "font-weight: bold; font-size: 17px; color: white; padding-right: 10px;"
        )
        self.layout.addWidget(self.group_label, alignment=Qt.AlignVCenter)

        self.btn_prev = QPushButton("◀")
        self.btn_prev.setCheckable(False)
        self.btn_prev.setMinimumSize(QSize(32, 40))
        self.btn_prev.setMaximumSize(QSize(32, 44))
        self.btn_prev.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_prev.setStyleSheet(
            "QPushButton {font-size: 18px; border-radius: 8px; border: 2px solid #ccc;"
            " background: #2a2c34; color: #b9d4ff;}"
            "QPushButton:hover {background: #51a4fc;}"
        )
        self.btn_prev.clicked.connect(lambda checked=False: self.prevClicked.emit())
        self.btn_prev.hide()
        self.layout.addWidget(self.btn_prev, alignment=Qt.AlignVCenter)

        self.group_btns_anchor = self.layout.count()

        self.btn_next = QPushButton("▶")
        self.btn_next.setCheckable(False)
        self.btn_next.setMinimumSize(QSize(32, 40))
        self.btn_next.setMaximumSize(QSize(32, 44))
        self.btn_next.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_next.setStyleSheet(
            "QPushButton {font-size: 18px; border-radius: 8px; border: 2px solid #ccc;"
            " background: #2a2c34; color: #b9d4ff;}"
            "QPushButton:hover {background: #51a4fc;}"
        )
        self.btn_next.clicked.connect(lambda checked=False: self.nextClicked.emit())
        self.btn_next.hide()
        self.layout.addWidget(self.btn_next, alignment=Qt.AlignVCenter)

        self.stretch = self.layout.addStretch(1)

        self.btn_process_group = QPushButton("📦 Process Group")
        self.btn_process_group.setToolTip(
            "Apply cleaning to the current group only."
        )

        self.btn_process_all = QPushButton("🚀 Process All")
        self.btn_process_all.setToolTip("Clean all loaded groups of videos.")

        for btn in (self.btn_process_group, self.btn_process_all):
            btn.setMinimumHeight(38)
            btn.setMinimumWidth(110)
            btn.setStyleSheet(
                "QPushButton { font-weight: 500; font-size: 14px;" +
                " border-radius: 8px; padding: 5px 10px; }"
            )
            self.layout.addWidget(btn, alignment=Qt.AlignRight)

        self.backend_combo = QComboBox(self)
        self.backend_combo.addItems(["mkvtoolnix", "ffmpeg"])
        self.backend_combo.setCurrentText(DEFAULTS.get("backend", "ffmpeg"))
        self.backend_combo.setToolTip("Select backend")
        self.backend_combo.currentTextChanged.connect(self.backendChanged.emit)
        self.backend_combo.setFixedHeight(32)
        self.layout.addWidget(self.backend_combo, alignment=Qt.AlignRight)

        self.btn_prefs = QPushButton("⚙️")
        self.btn_prefs.setMinimumSize(QSize(44, 42))
        self.btn_prefs.setMaximumSize(QSize(44, 42))
        self.btn_prefs.setToolTip("Preferences")
        self.btn_prefs.setStyleSheet(
            "QPushButton { font-size: 19px; border-radius: 8px; background: #20222a;"
            " color: #ccc; border: 2px solid #333; padding: 0; }"
            "QPushButton:hover { background: #363947; color: #fff;"
            " border: 2px solid #555; }"
        )
        self.layout.addWidget(self.btn_prefs, alignment=Qt.AlignRight)
        self.btn_prefs.clicked.connect(self.preferencesClicked.emit)

        self.setLayout(self.layout)
        self.setFixedHeight(54)

    def set_backend(self, backend: str):
        """Update dropdown to reflect the selected backend."""
        if backend not in {"mkvtoolnix", "ffmpeg"}:
            return
        self.backend_combo.blockSignals(True)
        self.backend_combo.setCurrentText(backend)
        self.backend_combo.blockSignals(False)

    def add_group_button(self, sig, tooltip=None):
        btn = QPushButton(str(len(self.group_buttons) + 1))
        btn.setCheckable(True)
        btn.setMinimumSize(QSize(48, 40))
        btn.setMaximumSize(QSize(48, 44))
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn.setStyleSheet(
            "QPushButton {font-weight: bold; font-size: 17px; border-radius: 8px;"
            " border: 2px solid #ccc; background: #2a2c34; color: #b9d4ff;}"
            "QPushButton:checked {background: #3584e4; color: white;"
            " border: 2px solid #1c71d8;}"
            "QPushButton:hover {background: #51a4fc;}"
        )
        if tooltip:
            btn.setToolTip(tooltip)
        self.layout.insertWidget(self.group_btns_anchor + len(self.group_buttons), btn)
        self.button_group.addButton(btn)
        self.group_buttons.append((sig, btn))
        return btn

    def update_button_tooltip(self, sig, tooltip):
        for s, b in self.group_buttons:
            if s == sig:
                b.setToolTip(tooltip)
                break

    def set_checked(self, idx):
        if 0 <= idx < len(self.group_buttons):
            self.group_buttons[idx][1].setChecked(True)

    def button_at(self, idx):
        return (
            self.group_buttons[idx][1] if 0 <= idx < len(self.group_buttons) else None
        )

    def sig_at(self, idx):
        return (
            self.group_buttons[idx][0] if 0 <= idx < len(self.group_buttons) else None
        )

    def clear(self):
        for _, btn in self.group_buttons:
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.group_buttons.clear()
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.update_nav_buttons(None)

    def update_nav_buttons(self, current_idx: int | None):
        """Show arrows when there are more than four groups and update their state."""
        show_arrows = len(self.group_buttons) > 4
        self.btn_prev.setVisible(show_arrows)
        self.btn_next.setVisible(show_arrows)
        if not show_arrows:
            return
        if current_idx is None:
            current_idx = -1
        self.btn_prev.setEnabled(current_idx > 0)
        self.btn_next.setEnabled(current_idx < len(self.group_buttons) - 1)
