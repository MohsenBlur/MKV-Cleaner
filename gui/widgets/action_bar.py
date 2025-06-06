from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PySide6.QtGui import QKeySequence

from .fade_disabled import apply_fade_on_disable


class ActionBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self.btn_open_files = QPushButton("📂 Open Files...")
        self.btn_open_files.setToolTip("Choose one or more MKV videos.")

        self.btn_def_audio = QPushButton("🔊 Default <b><u>A</u></b>udio")
        self.btn_def_audio.setToolTip(
            "Set which audio track should play by default."
        )
        self.btn_def_audio.setShortcut(QKeySequence("A"))

        self.btn_def_sub = QPushButton("💬 Default <b><u>S</u></b>ubtitle")
        self.btn_def_sub.setToolTip(
            "Set which subtitle track is shown automatically."
        )
        self.btn_def_sub.setShortcut(QKeySequence("S"))

        self.btn_forced = QPushButton("🏳️‍🌈 Set <b><u>F</u></b>orced")
        self.btn_forced.setToolTip(
            "Mark selected subtitles as forced so players show them."
        )
        self.btn_forced.setShortcut(QKeySequence("F"))

        self.btn_wipe_all = QPushButton("🧹 <b><u>W</u></b>ipe All Subs")
        self.btn_wipe_all.setToolTip("Remove every subtitle from these videos.")
        # Allow toggling so the state can be used when processing files
        self.btn_wipe_all.setCheckable(True)
        self.btn_wipe_all.setShortcut(QKeySequence("W"))
        self.btn_preview = QPushButton("👁️ <b><u>P</u></b>review Subtitle")
        self.btn_preview.setToolTip("Quickly check the subtitles before processing.")
        self.btn_preview.setShortcut(QKeySequence("P"))


        for btn in (
            self.btn_open_files,
            self.btn_def_audio,
            self.btn_def_sub,
            self.btn_forced,
            self.btn_wipe_all,
            self.btn_preview,
        ):
            btn.setMinimumHeight(38)
            btn.setMinimumWidth(110)
            btn.setStyleSheet(
                "QPushButton { font-weight: 500; font-size: 14px;" +
                " border-radius: 8px; padding: 5px 10px; }"
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
