from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton


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

        self.btn_def_audio = QPushButton("🔊 Default Audio")
        self.btn_def_audio.setToolTip(
            "Set which audio track should play by default."
        )

        self.btn_def_sub = QPushButton("💬 Default Subtitle")
        self.btn_def_sub.setToolTip(
            "Set which subtitle track is shown automatically."
        )

        self.btn_forced = QPushButton("🏳️‍🌈 Set Forced")
        self.btn_forced.setToolTip(
            "Mark selected subtitles as forced so players show them."
        )

        self.btn_wipe_all = QPushButton("🧹 Wipe All Subs")
        self.btn_wipe_all.setToolTip("Remove every subtitle from these videos.")
        # Allow toggling so the state can be used when processing files
        self.btn_wipe_all.setCheckable(True)
        self.btn_preview = QPushButton("👁️ Preview Subtitle")
        self.btn_preview.setToolTip("Quickly check the subtitles before processing.")


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
            layout.addWidget(btn)

        self.setLayout(layout)
        self.setFixedHeight(52)
