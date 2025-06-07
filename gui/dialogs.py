from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLineEdit,
    QCheckBox,
    QFileDialog,
    QDialogButtonBox,
    QPushButton,
    QWidget,
    QHBoxLayout,
    QComboBox,
    QLabel,
)
from PySide6.QtCore import QSettings
from PySide6.QtGui import QKeySequence, QShortcut


class HotkeysDialog(QDialog):
    def __init__(self, hotkeys: dict[str, list[str]], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hotkeys")
        layout = QFormLayout(self)
        for name, seqs in hotkeys.items():
            label = QLabel(", ".join(seqs), self)
            layout.addRow(f"{name}:", label)
        btn = QDialogButtonBox(QDialogButtonBox.Close, parent=self)
        btn.rejected.connect(self.reject)
        layout.addRow(btn)

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.settings = QSettings("MKVToolsCorp", "MKVCleaner")

        layout = QFormLayout(self)

        self.backend = QComboBox(self)
        self.backend.addItems(["mkvtoolnix", "ffmpeg"])
        self.backend.setCurrentText(self.settings.value("backend", "ffmpeg"))
        self.backend.setToolTip(
            "Select the underlying program used for processing your videos."
        )
        layout.addRow("Backend:", self.backend)

        self.merge_path = QLineEdit(self)
        self.merge_path.setText(self.settings.value("mkvmerge_cmd", "mkvmerge"))
        btn_m = QPushButton("…", self)
        btn_m.clicked.connect(lambda: self._pick_file(self.merge_path))
        self.merge_path.setToolTip("Path to the mkvmerge executable.")
        layout.addRow("mkvmerge command:", self._with_button(self.merge_path, btn_m))

        self.extract_path = QLineEdit(self)
        self.extract_path.setText(self.settings.value("mkvextract_cmd", "mkvextract"))
        btn_x = QPushButton("…", self)
        btn_x.clicked.connect(lambda: self._pick_file(self.extract_path))
        self.extract_path.setToolTip("Path to the mkvextract executable.")
        layout.addRow("mkvextract command:", self._with_button(self.extract_path, btn_x))

        self.ffmpeg_path = QLineEdit(self)
        self.ffmpeg_path.setText(self.settings.value("ffmpeg_cmd", "ffmpeg"))
        btn_fm = QPushButton("…", self)
        btn_fm.clicked.connect(lambda: self._pick_file(self.ffmpeg_path))
        self.ffmpeg_path.setToolTip("Path to the ffmpeg executable.")
        layout.addRow("ffmpeg command:", self._with_button(self.ffmpeg_path, btn_fm))

        self.ffprobe_path = QLineEdit(self)
        self.ffprobe_path.setText(self.settings.value("ffprobe_cmd", "ffprobe"))
        btn_fp = QPushButton("…", self)
        btn_fp.clicked.connect(lambda: self._pick_file(self.ffprobe_path))
        self.ffprobe_path.setToolTip("Path to the ffprobe executable.")
        layout.addRow("ffprobe command:", self._with_button(self.ffprobe_path, btn_fp))

        self.output_dir = QLineEdit(self)
        self.output_dir.setText(self.settings.value("output_dir", "cleaned"))
        self.output_dir.setToolTip(
            "Folder where cleaned files will be written. Can be relative to the source."
        )
        layout.addRow("Default output folder:", self.output_dir)

        self.wipe_all_def = QCheckBox(self)
        self.wipe_all_def.setChecked(self.settings.value("wipe_all_default", False, type=bool))
        self.wipe_all_def.setToolTip(
            "If checked, all subtitles will be removed unless you untoggle it."
        )
        layout.addRow("Wipe all subtitles by default:", self.wipe_all_def)

        sizes = [str(s) for s in range(10, 62, 2)]
        self.track_font_combo = QComboBox(self)
        self.track_font_combo.addItems(sizes)
        self.track_font_combo.setCurrentText(
            str(self.settings.value("track_font_size", 16))
        )
        self.track_font_combo.setToolTip("Change the font size used in the track list table.")
        layout.addRow("Track list font size:", self.track_font_combo)

        self.preview_font_combo = QComboBox(self)
        self.preview_font_combo.addItems(sizes)
        self.preview_font_combo.setCurrentText(
            str(self.settings.value("preview_font_size", 16))
        )
        self.preview_font_combo.setToolTip(
            "Font size for the subtitle preview window."
        )
        layout.addRow("Subtitle preview font size:", self.preview_font_combo)

        self.accent_edit = QLineEdit(self)
        self.accent_edit.setPlaceholderText("#RRGGBB or empty for random")
        self.accent_edit.setText(self.settings.value("accent_color", ""))
        self.accent_edit.setToolTip(
            "Color for buttons and highlights. Leave blank for a random color."
        )
        layout.addRow("Accent color:", self.accent_edit)

        self.btn_hotkeys = QPushButton("Hotkeys", self)
        self.btn_hotkeys.clicked.connect(self._open_hotkeys)
        self.btn_hotkeys.setToolTip("Show a list of available keyboard shortcuts.")
        layout.addRow(self.btn_hotkeys)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, parent=self)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)
        layout.addRow(self.buttons)

    def _with_button(self, widget, button):
        container = QWidget(self)
        h = QHBoxLayout(container)
        h.setContentsMargins(0, 0, 0, 0)
        h.addWidget(widget)
        h.addWidget(button)
        return container

    def _pick_file(self, line_edit: QLineEdit):
        path, _ = QFileDialog.getOpenFileName(self, "Select executable", "", "All Files (*)")
        if path:
            line_edit.setText(path)

    def accept(self) -> None:
        self.settings.setValue("backend", self.backend.currentText())
        self.settings.setValue("mkvmerge_cmd", self.merge_path.text())
        self.settings.setValue("mkvextract_cmd", self.extract_path.text())
        self.settings.setValue("ffmpeg_cmd", self.ffmpeg_path.text())
        self.settings.setValue("ffprobe_cmd", self.ffprobe_path.text())
        self.settings.setValue("output_dir", self.output_dir.text())
        self.settings.setValue("wipe_all_default", self.wipe_all_def.isChecked())
        self.settings.setValue("track_font_size", int(self.track_font_combo.currentText()))
        self.settings.setValue(
            "preview_font_size", int(self.preview_font_combo.currentText())
        )
        self.settings.setValue("accent_color", self.accent_edit.text())
        super().accept()

    def _open_hotkeys(self) -> None:
        parent = self.parent()
        hotkeys = {}
        if parent is not None and hasattr(parent, "hotkey_map"):
            for name, shortcuts in parent.hotkey_map.items():
                seqs = []
                for sc in shortcuts:
                    if isinstance(sc, QShortcut):
                        seqs.append(sc.key().toString(QKeySequence.NativeText))
                    else:
                        seqs.append(str(sc))
                hotkeys[name] = seqs
        dlg = HotkeysDialog(hotkeys, self)
        dlg.exec()
