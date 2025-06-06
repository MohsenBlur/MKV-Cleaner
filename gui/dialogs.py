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
)
from PySide6.QtCore import QSettings

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.settings = QSettings("MKVToolsCorp", "MKVCleaner")

        layout = QFormLayout(self)

        self.backend = QComboBox(self)
        self.backend.addItems(["mkvtoolnix", "ffmpeg"])
        self.backend.setCurrentText(self.settings.value("backend", "ffmpeg"))
        layout.addRow("Backend:", self.backend)

        self.merge_path = QLineEdit(self)
        self.merge_path.setText(self.settings.value("mkvmerge_cmd", "mkvmerge"))
        btn_m = QPushButton("…", self)
        btn_m.clicked.connect(lambda: self._pick_file(self.merge_path))
        layout.addRow("mkvmerge command:", self._with_button(self.merge_path, btn_m))

        self.extract_path = QLineEdit(self)
        self.extract_path.setText(self.settings.value("mkvextract_cmd", "mkvextract"))
        btn_x = QPushButton("…", self)
        btn_x.clicked.connect(lambda: self._pick_file(self.extract_path))
        layout.addRow("mkvextract command:", self._with_button(self.extract_path, btn_x))

        self.ffmpeg_path = QLineEdit(self)
        self.ffmpeg_path.setText(self.settings.value("ffmpeg_cmd", "ffmpeg"))
        btn_fm = QPushButton("…", self)
        btn_fm.clicked.connect(lambda: self._pick_file(self.ffmpeg_path))
        layout.addRow("ffmpeg command:", self._with_button(self.ffmpeg_path, btn_fm))

        self.ffprobe_path = QLineEdit(self)
        self.ffprobe_path.setText(self.settings.value("ffprobe_cmd", "ffprobe"))
        btn_fp = QPushButton("…", self)
        btn_fp.clicked.connect(lambda: self._pick_file(self.ffprobe_path))
        layout.addRow("ffprobe command:", self._with_button(self.ffprobe_path, btn_fp))

        self.output_dir = QLineEdit(self)
        self.output_dir.setText(self.settings.value("output_dir", "cleaned"))
        layout.addRow("Default output folder:", self.output_dir)

        self.wipe_all_def = QCheckBox(self)
        self.wipe_all_def.setChecked(self.settings.value("wipe_all_default", False, type=bool))
        layout.addRow("Wipe all subtitles by default:", self.wipe_all_def)

        sizes = [str(s) for s in range(10, 62, 2)]
        self.track_font_combo = QComboBox(self)
        self.track_font_combo.addItems(sizes)
        self.track_font_combo.setCurrentText(
            str(self.settings.value("track_font_size", 16))
        )
        layout.addRow("Track list font size:", self.track_font_combo)

        self.preview_font_combo = QComboBox(self)
        self.preview_font_combo.addItems(sizes)
        self.preview_font_combo.setCurrentText(
            str(self.settings.value("preview_font_size", 16))
        )
        layout.addRow("Subtitle preview font size:", self.preview_font_combo)

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
        super().accept()
