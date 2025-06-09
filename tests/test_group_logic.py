import os
import sys
from pathlib import Path

from core.tracks import Track
from core.config import AppConfig

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gui.group_logic import GroupLogic  # noqa: E402
import gui.group_logic as group_logic


class DummySignal:
    def __init__(self):
        self._cbs = []

    def connect(self, cb):
        self._cbs.append(cb)

    def emit(self, *args, **kwargs):
        for cb in list(self._cbs):
            cb(*args, **kwargs)


class DummyButton:
    def __init__(self):
        self.clicked = DummySignal()


class DummyGroupBar:
    def __init__(self):
        self.group_buttons = []
        self.prevClicked = DummySignal()
        self.nextClicked = DummySignal()

    def add_group_button(self, sig, tooltip=None):
        btn = DummyButton()
        self.group_buttons.append((sig, btn))
        return btn

    def remove_group_button(self, sig):
        for i, (s, _) in enumerate(self.group_buttons):
            if s == sig:
                self.group_buttons.pop(i)
                break

    def update_button_tooltip(self, sig, tooltip):
        pass

    def set_checked(self, idx):
        pass

    def sig_at(self, idx):
        return self.group_buttons[idx][0] if 0 <= idx < len(self.group_buttons) else None

    def clear(self):
        self.group_buttons.clear()

    def update_nav_buttons(self, idx):
        pass


class DummyModel:
    def __init__(self):
        self.updated = None

    def update_tracks(self, tracks):
        self.updated = tracks


class DummyTrackTable:
    def __init__(self):
        self.table_model = DummyModel()


def test_button_click_triggers_once(monkeypatch):
    logic = GroupLogic()
    logic.group_bar = DummyGroupBar()
    logic.track_table = DummyTrackTable()
    logic._setup_group_logic()
    logic.groups["sig1"] = []

    calls = []
    orig = logic._on_group_button_clicked

    def wrapper(btn):
        calls.append(btn)
        return orig(btn)

    monkeypatch.setattr(logic, "_on_group_button_clicked", wrapper)

    btn = logic.group_bar.add_group_button("sig1")
    btn.clicked.connect(lambda checked=False, b=btn: logic._on_group_button_clicked(b))

    btn.clicked.emit(False)

    assert len(calls) == 1


def test_empty_current_group():
    logic = GroupLogic()
    logic.group_bar = DummyGroupBar()
    logic.track_table = DummyTrackTable()
    logic.file_list = type("FL", (), {"update_files": lambda self, f: None, "clear": lambda self: None})()
    logic._setup_group_logic()
    logic.groups["sig1"] = []
    logic.file_groups["sig1"] = ["f1", "f2"]
    logic.current_sig = "sig1"

    logic._empty_current_group()

    assert "sig1" not in logic.file_groups
    assert "sig1" not in logic.groups
    assert logic.current_sig is None
    assert not logic.group_bar.group_buttons


def test_add_files_no_duplicates(monkeypatch):
    tracks = [Track(idx=0, tid=1, type="video", codec="h264", language="und", forced=False, name="")]

    monkeypatch.setattr(group_logic, "query_tracks", lambda p, cfg: tracks)

    logic = GroupLogic()
    logic.group_bar = DummyGroupBar()
    logic.track_table = DummyTrackTable()
    logic.file_list = type("FL", (), {"update_files": lambda self, f: None, "clear": lambda self: None})()
    logic.app_config = AppConfig()
    logic._setup_group_logic()

    logic.add_files_to_groups(["dup.mkv"])
    logic.add_files_to_groups(["dup.mkv"])

    sig = ";".join(t.signature() for t in tracks)
    assert len(logic.file_groups[sig]) == 1
    assert len(logic.group_bar.group_buttons) == 1


class DummyWipeButton:
    def __init__(self):
        self.checked = False

    def setChecked(self, val):
        self.checked = val

    def isChecked(self):
        return self.checked


class DummyActionBar:
    def __init__(self):
        self.btn_wipe_all = DummyWipeButton()


def test_delete_group_resets_wipe_all():
    logic = GroupLogic()
    logic.group_bar = DummyGroupBar()
    logic.track_table = DummyTrackTable()
    logic.action_bar = DummyActionBar()
    logic._setup_group_logic()

    logic.groups["sig1"] = []
    logic.file_groups["sig1"] = ["f1"]
    logic.current_sig = "sig1"
    logic.group_bar.add_group_button("sig1")

    logic.action_bar.btn_wipe_all.setChecked(True)

    logic._empty_current_group()

    assert logic.action_bar.btn_wipe_all.isChecked() is False
