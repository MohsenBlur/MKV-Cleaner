from PySide6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QFileDialog,
    QStatusBar,
)
from PySide6.QtCore import QSettings
import os

from gui.widgets.group_bar import GroupBar
from gui.widgets.action_bar import ActionBar
from gui.widgets.track_table import TrackTable

from .settings_logic import SettingsLogic
from .group_logic import GroupLogic
from .table_logic import TableLogic
from .actions_logic import ActionsLogic


class MainWindow(QMainWindow, SettingsLogic, GroupLogic, TableLogic, ActionsLogic):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MKV Cleaner")
        self.resize(1200, 750)

        self.settings = QSettings("MKVToolsCorp", "MKVCleaner")
        self.last_dir = self.settings.value("last_dir", os.path.expanduser("~"))

        self.group_bar = GroupBar(self)
        self.action_bar = ActionBar(self)
        self.track_table = TrackTable(self)
        self.status_bar = QStatusBar(self)
        self.status_bar.setSizeGripEnabled(False)

        main_vbox = QVBoxLayout()
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)
        main_vbox.addWidget(self.group_bar)
        main_vbox.addWidget(self.track_table)
        main_vbox.addWidget(self.status_bar)
        main_vbox.addWidget(self.action_bar)

        container = QWidget()
        container.setLayout(main_vbox)
        self.setCentralWidget(container)

        self.group_bar.preferencesClicked.connect(self._open_preferences)
        self._setup_all_logic()

    def _setup_all_logic(self):
        self._setup_settings_logic()
        self._setup_group_logic()
        self._setup_table_logic()
        self._setup_action_logic()

    def open_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Open MKV Files", self.last_dir, "Matroska Video Files (*.mkv)"
        )
        if files:
            self.last_dir = os.path.dirname(files[0])
            self.settings.setValue("last_dir", self.last_dir)
            self.add_files_to_groups(files)

