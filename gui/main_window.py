from PySide6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QFileDialog
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

        main_vbox = QVBoxLayout()
        main_vbox.setContentsMargins(0, 0, 0, 0)
        main_vbox.setSpacing(0)
        main_vbox.addWidget(self.group_bar)
        main_vbox.addWidget(self.track_table)
        main_vbox.addWidget(self.action_bar)

        container = QWidget()
        container.setLayout(main_vbox)
        self.setCentralWidget(container)

        self.group_bar.preferencesClicked.connect(self._open_preferences)
        self.group_bar.button_group.buttonClicked.connect(self.on_group_button_clicked)
        self._setup_all_logic()

        self.groups = []  # Each group: {'name': ..., 'tracks': [...]}
        self.current_group = None

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
            self.load_files(files)

    def load_files(self, files):
        for f in files:
            group_idx = self.add_group(f)
            tracks = self.parse_tracks(f)
            self.add_tracks_to_group(group_idx, tracks)
            print(f"Added file '{f}' as group {group_idx}, tracks: {tracks}")
        self.current_group = 0 if self.groups else None
        self.update_group_display()

    def add_group(self, filename):
        group = {"name": os.path.basename(filename), "filename": filename, "tracks": []}
        self.groups.append(group)
        idx = len(self.groups) - 1
        self.group_bar.add_group_button(sig=idx, tooltip=filename)
        return idx

    def parse_tracks(self, filename):
        # Dummy logic: Replace with your actual mkv parsing
        # If you have a real track parser, plug it in here.
        from collections import namedtuple

        DummyTrack = namedtuple(
            "Track",
            [
                "tid",
                "type",
                "codec",
                "language",
                "forced",
                "default_audio",
                "default_subtitle",
                "name",
                "removed",
            ],
        )
        return [
            DummyTrack(
                0,
                "video",
                "V_MPEG4",
                "und",
                False,
                False,
                False,
                os.path.basename(filename),
                False,
            ),
            DummyTrack(1, "audio", "A_AAC", "eng", False, True, False, "", False),
            DummyTrack(
                2, "subtitles", "S_TEXT/ASS", "eng", False, False, True, "", False
            ),
        ]

    def add_tracks_to_group(self, group_idx, tracks):
        self.groups[group_idx]["tracks"] = tracks

    def update_group_display(self):
        # Update table to show tracks for the current group
        if self.groups and self.current_group is not None:
            tracks = self.groups[self.current_group]["tracks"]
            self.track_table.model.update_tracks(tracks)
        else:
            self.track_table.model.update_tracks([])

    def on_group_button_clicked(self, btn):
        # Find which group button was clicked and update display
        idx = None
        for i, (_, b) in enumerate(self.group_bar.group_buttons):
            if b is btn:
                idx = i
                break
        if idx is not None:
            self.current_group = idx
            self.update_group_display()

    def _open_preferences(self):
        print("Preferences dialog opened")  # Implement dialog if needed
