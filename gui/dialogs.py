# gui/dialogs.py

from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QCheckBox, QFileDialog,
    QDialogButtonBox, QPushButton, QWidget, QHBoxLayout
)
from PySide6.QtCore import QSettings

class PreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self.settings = QSettings("MKVToolsCorp", "MKVCleaner")

        layout = QFormLayout(self)

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

        self.output_dir = QLineEdit(self)
        self.output_dir.setText(self.settings.value("output_dir", "cleaned"))
        layout.addRow("Default output folder:", self.output_dir)

        self.wipe_all_def = QCheckBox(self)
        self.wipe_all_def.setChecked(self.settings.value("wipe_all_default", False, type=bool))
        layout.addRow("Wipe all subtitles by default:", self.wipe_all_def)

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
        self.settings.setValue("mkvmerge_cmd", self.merge_path.text())
        self.settings.setValue("mkvextract_cmd", self.extract_path.text())
        self.settings.setValue("output_dir", self.output_dir.text())
        self.settings.setValue("wipe_all_default", self.wipe_all_def.isChecked())
        super().accept()
