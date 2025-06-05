"""Widgets providing top-level actions for the application."""

from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton


class ActionBar(QWidget):
    """Horizontal bar with buttons for actions like processing files."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 4, 8, 4)
        layout.setSpacing(8)

        self.btn_open_files = QPushButton("📂 Open Files...")
        self.btn_def_audio = QPushButton("🔊 Default Audio")
        self.btn_def_sub = QPushButton("💬 Default Subtitle")
        self.btn_forced = QPushButton("🏳️‍🌈 Set Forced")
        self.btn_wipe_all = QPushButton("🧹 Wipe All Subs")
        # Allow toggling so the state can be used when processing files
        self.btn_wipe_all.setCheckable(True)
        self.btn_preview = QPushButton("👁️ Preview Subtitle")
        self.btn_process_group = QPushButton("📦 Process Group")
        self.btn_process_all = QPushButton("🚀 Process All")

        for btn in (
            self.btn_open_files,
            self.btn_def_audio,
            self.btn_def_sub,
            self.btn_forced,
            self.btn_wipe_all,
            self.btn_preview,
            self.btn_process_group,
            self.btn_process_all,
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
