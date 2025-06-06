from PySide6.QtCore import QSettings
from gui.dialogs import PreferencesDialog
from core.config import load_config, DEFAULTS

class SettingsLogic:
    def _setup_settings_logic(self):
        self.settings = QSettings("MKVToolsCorp", "MKVCleaner")
        self._load_preferences()

        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_prefs"):
            self.action_bar.btn_prefs.clicked.connect(self._open_preferences)
        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_wipe_all"):
            # Initialise wipe all toggle with stored preference
            self.action_bar.btn_wipe_all.setChecked(self.wipe_all_default)
        if hasattr(self, "menu_preferences"):
            self.menu_preferences.triggered.connect(self._open_preferences)
        if hasattr(self, "group_bar") and hasattr(self.group_bar, "backend_combo"):
            self.group_bar.set_backend(DEFAULTS.get("backend", "ffmpeg"))
            self.group_bar.backendChanged.connect(self._change_backend)

    def _load_preferences(self):
        prefs = load_config()
        prefs["backend"]        = self.settings.value("backend", prefs["backend"])
        prefs["mkvmerge_cmd"]   = self.settings.value("mkvmerge_cmd", prefs["mkvmerge_cmd"])
        prefs["mkvextract_cmd"] = self.settings.value("mkvextract_cmd", prefs["mkvextract_cmd"])
        prefs["ffmpeg_cmd"]     = self.settings.value("ffmpeg_cmd", prefs["ffmpeg_cmd"])
        prefs["ffprobe_cmd"]    = self.settings.value("ffprobe_cmd", prefs["ffprobe_cmd"])
        prefs["output_dir"]      = self.settings.value("output_dir", prefs["output_dir"])
        prefs["track_font_size"] = int(
            self.settings.value("track_font_size", prefs.get("track_font_size", 16))
        )
        if prefs["track_font_size"] < 10:
            prefs["track_font_size"] = 10
        prefs["preview_font_size"] = int(
            self.settings.value("preview_font_size", prefs.get("preview_font_size", 16))
        )
        if prefs["preview_font_size"] < 10:
            prefs["preview_font_size"] = 10
        DEFAULTS.update(prefs)
        if hasattr(self, "track_table"):
            size = DEFAULTS.get("track_font_size", 16)
            self.track_table.setStyleSheet(f"font-size: {size}px;")
            self.track_table.horizontalHeader().setStyleSheet(
                f"font-size: {size}px; font-weight: bold;"
            )
            if hasattr(self.track_table, "_apply_row_spacing"):
                self.track_table._apply_row_spacing()
        self.last_input_dir   = self.settings.value("last_input_dir", "", type=str)
        self.wipe_all_default = self.settings.value("wipe_all_default", False, type=bool)
        if hasattr(self, "group_bar") and hasattr(self.group_bar, "set_backend"):
            self.group_bar.set_backend(DEFAULTS.get("backend", "ffmpeg"))

    def _open_preferences(self):
        dlg = PreferencesDialog(self)
        if dlg.exec():
            self._load_preferences()
            if hasattr(self.action_bar, "btn_wipe_all"):
                self.action_bar.btn_wipe_all.setChecked(self.wipe_all_default)

    def _change_backend(self, backend: str):
        DEFAULTS["backend"] = backend
        self.settings.setValue("backend", backend)
        if hasattr(self, "_reload_all_groups"):
            self._reload_all_groups()

    def closeEvent(self, event):
        if hasattr(self, "track_table") and hasattr(self.track_table, "horizontalHeader"):
            self.settings.setValue("header_state", self.track_table.horizontalHeader().saveState())
        if getattr(self, "last_input_dir", None):
            self.settings.setValue("last_input_dir", self.last_input_dir)
        super().closeEvent(event)
