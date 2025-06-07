from PySide6.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QButtonGroup,
    QSizePolicy,
    QComboBox,
    QDialog,
    QGridLayout,
)
from PySide6.QtCore import Qt, QSize, Signal, QPoint

from .fade_disabled import apply_fade_on_disable


class GroupDrawer(QDialog):
    """Popup dialog listing all group buttons."""

    def __init__(self, bar: "GroupBar"):
        super().__init__(bar)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setObjectName("GroupDrawer")
        self.setStyleSheet(
            "#GroupDrawer {"
            " background: #20222a;"
            " border: 2px solid #333;"
            " border-radius: 8px;"
            " }"
        )
        self.bar = bar
        layout = QGridLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setHorizontalSpacing(6)
        layout.setVerticalSpacing(6)
        for idx, (_, btn) in enumerate(bar.group_buttons):
            b = QPushButton(btn.text(), self)
            b.setFixedSize(btn.size())
            b.setStyleSheet(btn.styleSheet())
            b.clicked.connect(lambda checked=False, i=idx: self._choose(i))
            row, col = divmod(idx, 4)
            layout.addWidget(b, row, col)

    def _choose(self, idx: int):
        btn = self.bar.button_at(idx)
        if btn is not None:
            btn.click()
        self.accept()


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
        # Match the left margin of the action bar so the Groups button lines up
        # with the Open Files button
        self.layout.setContentsMargins(8, 4, 16, 4)
        self.layout.setSpacing(14)

        self.btn_groups = QPushButton("Groups")
        self.btn_groups.setCheckable(False)
        self.btn_groups.setMinimumHeight(38)
        self.btn_groups.setMinimumWidth(110)
        self.btn_groups.setStyleSheet(
            "QPushButton { font-weight: 500; font-size: 14px;"
            " border-radius: 8px; padding: 5px 10px; }"
        )
        apply_fade_on_disable(self.btn_groups)
        self.btn_groups.setToolTip(
            "Open a popup listing every group of videos."
        )
        self.btn_groups.clicked.connect(self._open_drawer)
        self.layout.addWidget(self.btn_groups, alignment=Qt.AlignVCenter)

        # Use plain arrow characters so they are visible without color emoji support
        self.btn_prev = QPushButton("⬅")
        self.btn_prev.setCheckable(False)
        self.btn_prev.setMinimumSize(QSize(32, 40))
        self.btn_prev.setMaximumSize(QSize(32, 44))
        self.btn_prev.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_prev.setStyleSheet(
            "QPushButton {font-size: 18px; border-radius: 8px; border: 2px solid #ccc;"
            " background: #2a2c34; color: #b9d4ff;}"
            "QPushButton:hover {background: #51a4fc;}"
        )
        apply_fade_on_disable(self.btn_prev)
        self.btn_prev.setToolTip(
            "Go to the previous group of videos that share the same track layout."
        )
        self.btn_prev.clicked.connect(lambda checked=False: self.prevClicked.emit())
        self.btn_prev.hide()

        # container holding the numbered group buttons
        self.group_btn_container = QWidget(self)
        self.group_btns_layout = QHBoxLayout(self.group_btn_container)
        self.group_btns_layout.setContentsMargins(0, 0, 0, 0)
        self.group_btns_layout.setSpacing(6)

        self.btn_next = QPushButton("➡")
        self.btn_next.setCheckable(False)
        self.btn_next.setMinimumSize(QSize(32, 40))
        self.btn_next.setMaximumSize(QSize(32, 44))
        self.btn_next.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.btn_next.setStyleSheet(
            "QPushButton {font-size: 18px; border-radius: 8px; border: 2px solid #ccc;"
            " background: #2a2c34; color: #b9d4ff;}"
            "QPushButton:hover {background: #51a4fc;}"
        )
        apply_fade_on_disable(self.btn_next)
        self.btn_next.setToolTip(
            "Go to the next group of videos that share the same track layout."
        )
        self.btn_next.clicked.connect(lambda checked=False: self.nextClicked.emit())
        self.btn_next.hide()

        # Keep prev/next arrows close to the group buttons by using a
        # sub-layout that matches the spacing of the group buttons
        self.nav_layout = QHBoxLayout()
        self.nav_layout.setContentsMargins(0, 0, 0, 0)
        self.nav_layout.setSpacing(6)
        self.nav_layout.addWidget(self.btn_prev, alignment=Qt.AlignVCenter)
        self.nav_layout.addWidget(self.group_btn_container, alignment=Qt.AlignVCenter)
        self.nav_layout.addWidget(self.btn_next, alignment=Qt.AlignVCenter)
        self.layout.addLayout(self.nav_layout)

        self.stretch = self.layout.addStretch(1)

        self.btn_process_group = QPushButton("📦 Process Group")
        self.btn_process_group.setToolTip(
            "Clean only the videos in the group that is currently selected."
        )

        self.btn_process_all = QPushButton("🚀 Process All")
        self.btn_process_all.setToolTip(
            "Clean every loaded group of videos in one go."
        )

        # Keep right side controls close together similar to the action bar
        self.right_layout = QHBoxLayout()
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        # Match the spacing used in ActionBar
        self.right_layout.setSpacing(8)

        for btn in (self.btn_process_group, self.btn_process_all):
            btn.setMinimumHeight(38)
            btn.setMinimumWidth(110)
            btn.setStyleSheet(
                "QPushButton { font-weight: 500; font-size: 14px;" +
                " border-radius: 8px; padding: 5px 10px; }"
            )
            apply_fade_on_disable(btn)
            self.right_layout.addWidget(btn)

        self.backend_combo = QComboBox(self)
        self.backend_combo.addItems(["mkvtoolnix", "ffmpeg"])
        self.backend_combo.setCurrentText("ffmpeg")
        self.backend_combo.setToolTip(
            "Choose which program is used for cleaning: MKVToolNix or FFmpeg."
        )
        self.backend_combo.currentTextChanged.connect(self.backendChanged.emit)
        self.backend_combo.setMinimumHeight(38)
        self.backend_combo.setStyleSheet("QComboBox { font-size: 14px; }")
        self.right_layout.addWidget(self.backend_combo)

        self.btn_prefs = QPushButton("⚙️")
        self.btn_prefs.setMinimumSize(QSize(44, 42))
        self.btn_prefs.setMaximumSize(QSize(44, 42))
        self.btn_prefs.setToolTip(
            "Open the preferences window to change paths, fonts and other options."
        )
        self.btn_prefs.setStyleSheet(
            "QPushButton { font-size: 19px; border-radius: 8px; background: #20222a;"
            " color: #ccc; border: 2px solid #333; padding: 0; }"
            "QPushButton:hover { background: #363947; color: #fff;"
            " border: 2px solid #555; }"
        )
        apply_fade_on_disable(self.btn_prefs)
        self.right_layout.addWidget(self.btn_prefs)
        self.btn_prefs.clicked.connect(self.preferencesClicked.emit)

        self.layout.addLayout(self.right_layout)

        self.setLayout(self.layout)
        self.setFixedHeight(54)

    def _open_drawer(self):
        if len(self.group_buttons) <= 4:
            return
        dlg = GroupDrawer(self)
        base_pos = self.mapToGlobal(self.rect().topLeft())
        left = self.group_btn_container.mapToGlobal(
            self.group_btn_container.rect().topLeft()
        ).x() - 10
        pos = QPoint(left, base_pos.y())
        dlg.move(pos)
        dlg.exec()

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
        apply_fade_on_disable(btn)
        if tooltip:
            btn.setToolTip(tooltip)
        self.group_btns_layout.addWidget(btn)
        self.button_group.addButton(btn)
        self.group_buttons.append((sig, btn))
        return btn

    def remove_group_button(self, sig):
        for i, (s, btn) in enumerate(self.group_buttons):
            if s == sig:
                self.group_btns_layout.removeWidget(btn)
                btn.deleteLater()
                self.button_group.removeButton(btn)
                self.group_buttons.pop(i)
                break
        for j, (_, b) in enumerate(self.group_buttons):
            b.setText(str(j + 1))
        self.update_nav_buttons(None)

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
            self.group_btns_layout.removeWidget(btn)
            btn.deleteLater()
        self.group_buttons.clear()
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.update_nav_buttons(None)

    def update_nav_buttons(self, current_idx: int | None):
        """Update arrow states and which group buttons are visible."""
        total = len(self.group_buttons)
        show_arrows = total > 4
        self.btn_prev.setVisible(show_arrows)
        self.btn_next.setVisible(show_arrows)
        self.btn_groups.setEnabled(show_arrows)

        for _, b in self.group_buttons:
            b.hide()

        if total == 0:
            return

        if current_idx is None or current_idx < 0:
            current_idx = 0

        start = max(0, current_idx - 1)
        end = start + 4
        if end > total:
            end = total
            start = max(0, end - 4)

        for i in range(start, end):
            self.group_buttons[i][1].show()

        if show_arrows:
            self.btn_prev.setEnabled(current_idx > 0)
            self.btn_next.setEnabled(current_idx < total - 1)
