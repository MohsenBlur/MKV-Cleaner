import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from gui.group_logic import GroupLogic  # noqa: E402


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
