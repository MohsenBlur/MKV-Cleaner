from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel, QPushButton, QButtonGroup, QSizePolicy
from PySide6.QtCore import Qt, QSize, Signal

class GroupBar(QWidget):
    preferencesClicked = Signal()

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

        self.group_btns_anchor = self.layout.count()
        self.stretch = self.layout.addStretch(1)

        self.btn_prefs = QPushButton("⚙️")
        self.btn_prefs.setMinimumSize(QSize(44, 42))
        self.btn_prefs.setMaximumSize(QSize(44, 42))
        self.btn_prefs.setToolTip("Preferences")
        self.btn_prefs.setStyleSheet(
            "QPushButton { font-size: 19px; border-radius: 8px; background: #20222a; color: #ccc; border: 2px solid #333; padding: 0; }"
            "QPushButton:hover { background: #363947; color: #fff; border: 2px solid #555; }"
        )
        self.layout.addWidget(self.btn_prefs, alignment=Qt.AlignRight)
        self.btn_prefs.clicked.connect(self.preferencesClicked.emit)

        self.setLayout(self.layout)
        self.setFixedHeight(54)

    def add_group_button(self, sig, tooltip=None):
        btn = QPushButton(str(len(self.group_buttons) + 1))
        btn.setCheckable(True)
        btn.setMinimumSize(QSize(48, 40))
        btn.setMaximumSize(QSize(48, 44))
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        btn.setStyleSheet(
            "QPushButton {font-weight: bold; font-size: 17px; border-radius: 8px; border: 2px solid #ccc; background: #2a2c34; color: #b9d4ff;}"
            "QPushButton:checked {background: #3584e4; color: white; border: 2px solid #1c71d8;}"
            "QPushButton:hover {background: #51a4fc;}"
        )
        if tooltip:
            btn.setToolTip(tooltip)
        self.layout.insertWidget(1 + len(self.group_buttons), btn)
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
        return self.group_buttons[idx][1] if 0 <= idx < len(self.group_buttons) else None

    def sig_at(self, idx):
        return self.group_buttons[idx][0] if 0 <= idx < len(self.group_buttons) else None

    def clear(self):
        for _, btn in self.group_buttons:
            self.layout.removeWidget(btn)
            btn.deleteLater()
        self.group_buttons.clear()
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
