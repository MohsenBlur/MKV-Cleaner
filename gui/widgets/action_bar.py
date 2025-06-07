from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt
from ..theme import FONT_SIZES, SIZES

from .fade_disabled import apply_fade_on_disable


class ActionBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(
            SIZES['margin_h'], SIZES['margin_v'], SIZES['margin_h'], SIZES['margin_v']
        )
        layout.setSpacing(SIZES['spacing'])

        self.btn_open_files = QPushButton("📂 Open Files...")
        self.btn_open_files.setToolTip(
            "Load MKV files into the program so you can clean them."
        )

        # Use ampersand to mark shortcut letters
        self.btn_def_audio = QPushButton("🔊 Default &Audio")
        self.btn_def_audio.setToolTip(
            "Pick an audio track in the list and mark it as the default track."
        )

        self.btn_def_sub = QPushButton("💬 Default &Subtitle")
        self.btn_def_sub.setToolTip(
            "Pick a subtitle track and make it show by default when the video plays."
        )

        self.btn_forced = QPushButton("🏳️‍🌈 Set &Forced")
        self.btn_forced.setToolTip(
            "Mark a subtitle track as forced so video players always display it."
        )

        self.btn_wipe_all = QPushButton("🧹 &Wipe All Subs")
        self.btn_wipe_all.setToolTip(
            "Toggle to remove all subtitle tracks from the cleaned videos."
        )
        # Allow toggling so the state can be used when processing files
        self.btn_wipe_all.setCheckable(True)
        self.btn_preview = QPushButton("👁️ &Preview Subtitle")
        self.btn_preview.setToolTip(
            "Open a window to quickly view the subtitle text before cleaning."
        )


        for btn in (
            self.btn_open_files,
            self.btn_def_audio,
            self.btn_def_sub,
            self.btn_forced,
            self.btn_wipe_all,
            self.btn_preview,
        ):
            btn.setMinimumHeight(SIZES['button_height'])
            btn.setMinimumWidth(SIZES['button_min_width'])
            btn.setFocusPolicy(Qt.NoFocus)
            btn.setStyleSheet(
                f"QPushButton {{ font-weight: 500; font-size: {FONT_SIZES['small']}px;"
                f" border-radius: {SIZES['border_radius']}px; padding: {SIZES['button_padding']}; }}"
            )
            apply_fade_on_disable(btn)
            layout.addWidget(btn)

        self.setLayout(layout)
        self.setFixedHeight(52)

    def required_width(self) -> int:
        """Return the minimum width needed to show all buttons without cutting off."""
        layout = self.layout()
        if layout is None:
            return 0
        margins = layout.contentsMargins()
        spacing = layout.spacing()
        widths = []
        for i in range(layout.count()):
            item = layout.itemAt(i)
            w = item.widget() if item else None
            if w is not None:
                widths.append(w.sizeHint().width())
        if not widths:
            return 0
        total = sum(widths) + spacing * (len(widths) - 1)
        total += margins.left() + margins.right()
        return total
