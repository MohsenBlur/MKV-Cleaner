from PySide6.QtCore import QSettings
from gui.dialogs import PreferencesDialog
from core.config import load_config, DEFAULTS

class SettingsLogic:
    def _setup_settings_logic(self):
        self.settings = QSettings("MKVToolsCorp", "MKVCleaner")
        self._load_preferences()

        if hasattr(self, "action_bar") and hasattr(self.action_bar, "btn_prefs"):
            self.action_bar.btn_prefs.clicked.connect(self._open_preferences)
        if hasattr(self, "menu_preferences"):
            self.menu_preferences.triggered.connect(self._open_preferences)

    def _load_preferences(self):
        prefs = load_config()
        prefs["mkvmerge_cmd"]   = self.settings.value("mkvmerge_cmd", prefs["mkvmerge_cmd"])
        prefs["mkvextract_cmd"] = self.settings.value("mkvextract_cmd", prefs["mkvextract_cmd"])
        prefs["output_dir"]     = self.settings.value("output_dir", prefs["output_dir"])
        DEFAULTS.update(prefs)
        self.last_input_dir   = self.settings.value("last_input_dir", "", type=str)
        self.wipe_all_default = self.settings.value("wipe_all_default", False, type=bool)

    def _open_preferences(self):
        dlg = PreferencesDialog(self)
        if dlg.exec():
            self._load_preferences()
            if hasattr(self.action_bar, "btn_wipe_all"):
                self.action_bar.btn_wipe_all.setChecked(self.wipe_all_default)

    def closeEvent(self, event):
        if hasattr(self, "track_table") and hasattr(self.track_table, "horizontalHeader"):
            self.settings.setValue("header_state", self.track_table.horizontalHeader().saveState())
        if getattr(self, "last_input_dir", None):
            self.settings.setValue("last_input_dir", self.last_input_dir)
        super().closeEvent(event)
