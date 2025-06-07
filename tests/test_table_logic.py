import types
import sys

# Stub PySide6 modules
sys.modules['PySide6'] = types.ModuleType('PySide6')
qtcore = types.ModuleType('PySide6.QtCore')
qtcore.Qt = type('Qt', (), {})
sys.modules['PySide6.QtCore'] = qtcore

from gui.table_logic import TableLogic
from core.tracks import Track

class DummyButton:
    def __init__(self):
        self.enabled = False
    def setEnabled(self, val):
        self.enabled = val
    def isEnabled(self):
        return self.enabled

class DummyActionBar:
    def __init__(self):
        self.btn_def_audio = DummyButton()
        self.btn_def_sub = DummyButton()
        self.btn_forced = DummyButton()
        self.btn_wipe_all = DummyButton()
        self.btn_preview = DummyButton()

class DummyModel:
    def __init__(self, tracks):
        self.tracks = tracks
    def update_tracks(self, tracks):
        self.tracks = tracks
    def track_at_row(self, row):
        return self.tracks[row]
    def get_tracks(self):
        return self.tracks

class DummyTrackTable:
    def __init__(self, tracks):
        self.table_model = DummyModel(tracks)

class DummyIndex:
    def __init__(self, valid=False, row=0):
        self._valid = valid
        self._row = row
    def isValid(self):
        return self._valid
    def row(self):
        return self._row

class DummyWindow(TableLogic):
    def __init__(self, tracks):
        self.action_bar = DummyActionBar()
        self.track_table = DummyTrackTable(tracks)
        self.groups = {"g1": tracks}
        self.current_sig = "g1"

def test_wipe_all_enabled_without_selection():
    tracks = [
        Track(idx=0, tid=1, type="subtitles", codec="srt", language="eng", forced=False, name="Eng"),
        Track(idx=1, tid=2, type="audio", codec="aac", language="eng", forced=False, name="Au"),
    ]
    win = DummyWindow(tracks)
    win._on_selection_change(DummyIndex(valid=False), None)
    assert win.action_bar.btn_wipe_all.isEnabled() is True
