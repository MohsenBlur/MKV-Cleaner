import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import types

sys.modules["PySide6"] = types.ModuleType("PySide6")
qtcore = types.ModuleType("PySide6.QtCore")
qtcore.QMetaObject = type("QMetaObject", (), {"invokeMethod": lambda *a, **k: None})
qtcore.Q_ARG = lambda typ, val: val
qtcore.Qt = type(
    "Qt", (), {"WindowModal": 0, "ApplicationModal": 1, "QueuedConnection": 0}
)
sys.modules["PySide6.QtCore"] = qtcore

qtwidgets = types.ModuleType("PySide6.QtWidgets")
qtwidgets.LogoSplash = object
qtwidgets.QSplashScreen = object
qtwidgets.QWidget = object
qtwidgets.QLabel = object
qtwidgets.QVBoxLayout = object
qtwidgets.QMessageBox = type(
    "QMessageBox",
    (),
    {
        "warning": staticmethod(lambda *a, **k: None),
        "information": staticmethod(lambda *a, **k: None),
        "question": staticmethod(lambda *a, **k: qtwidgets.QMessageBox.Yes),
        "Yes": 1,
        "No": 0,
    },
)
sys.modules["PySide6.QtWidgets"] = qtwidgets
qtgui = types.ModuleType("PySide6.QtGui")
qtgui.QPixmap = object
sys.modules["PySide6.QtGui"] = qtgui

import importlib
import gui.processing as processing  # noqa: E402

processing = importlib.reload(processing)


class DummyDialog:
    def __init__(self):
        self._val = 0
        self._canceled = False

    def setWindowModality(self, *a):
        pass

    def setMinimumDuration(self, *a):
        pass

    def setValue(self, val):
        self._val = val
        if val >= 1:
            self._canceled = True

    def wasCanceled(self):
        return self._canceled

    def close(self):
        pass

    def show(self):
        pass

    def activateWindow(self):
        pass


class DummyExecutor:
    def __init__(self, *a, **kw):
        self.shutdown_called = {}
        self.tasks = []

    def submit(self, fn, *args, **kwargs):
        fut = DummyFuture(fn, *args, **kwargs)
        self.tasks.append(fut)
        return fut

    def shutdown(self, wait=True, cancel_futures=False):
        self.shutdown_called = {"wait": wait, "cancel_futures": cancel_futures}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if not self.shutdown_called:
            self.shutdown()


class DummyFuture:
    def __init__(self, fn, *args, **kwargs):
        self.fn = fn
        self.args = args
        self.kw = kwargs
        self._result = None

    def run(self):
        self._result = self.fn(*self.args, **self.kw)

    def result(self):
        if self._result is None:
            self.run()
        return self._result


def dummy_as_completed(futures):
    for f in futures:
        f.run()
        yield f


def test_cancel_shutdown(monkeypatch):
    jobs = [(Path("a"), []), (Path("b"), [])]
    commands = []

    def query_tracks(src):
        return []

    def build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=False):
        return ["cmd", str(src), str(dst)]

    def run_command(cmd, capture=True):
        commands.append((cmd, capture))

    exec_instance = DummyExecutor()
    monkeypatch.setattr(
        processing, "ThreadPoolExecutor", lambda *a, **kw: exec_instance
    )
    monkeypatch.setattr(processing, "as_completed", dummy_as_completed)

    processing.process_files(
        jobs,
        max_workers=2,
        query_tracks=query_tracks,
        build_cmd=build_cmd,
        run_command=run_command,
        output_dir="out",
        wipe_all_flag=False,
    )

    assert len(commands) == 2
    assert commands[0][1] is False
    assert commands[1][1] is False
    assert exec_instance.shutdown_called == {"wait": True, "cancel_futures": False}


def test_output_dir_created(monkeypatch, tmp_path):
    jobs = [(tmp_path / "a.mkv", [])]
    commands = []

    def query_tracks(src):
        return []

    def build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=False):
        return ["cmd", str(src), str(dst)]

    def run_command(cmd, capture=True):
        commands.append((cmd, capture))

    exec_instance = DummyExecutor()
    monkeypatch.setattr(
        processing, "ThreadPoolExecutor", lambda *a, **kw: exec_instance
    )
    monkeypatch.setattr(processing, "as_completed", dummy_as_completed)

    processing.process_files(
        jobs,
        max_workers=2,
        query_tracks=query_tracks,
        build_cmd=build_cmd,
        run_command=run_command,
        output_dir="out/sub",
        wipe_all_flag=False,
    )

    assert (tmp_path / "out" / "sub").is_dir()
    assert commands and commands[0][1] is False


def test_overwrite_prompt_cancel(monkeypatch, tmp_path):
    src = tmp_path / "a.mkv"
    src.write_text("data")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "a.mkv").write_text("old")

    jobs = [(src, [])]
    commands = []

    def query_tracks(src):
        return []

    def build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=False):
        return ["cmd", str(src), str(dst)]

    def run_command(cmd, capture=True):
        commands.append(cmd)

    exec_instance = DummyExecutor()
    monkeypatch.setattr(processing, "ThreadPoolExecutor", lambda *a, **kw: exec_instance)
    monkeypatch.setattr(processing, "as_completed", dummy_as_completed)
    monkeypatch.setattr(processing.QMessageBox, "question", lambda *a, **k: processing.QMessageBox.No)

    parent = type("P", (), {"setEnabled": lambda self, val: None})()
    processing.process_files(
        jobs,
        max_workers=1,
        query_tracks=query_tracks,
        build_cmd=build_cmd,
        run_command=run_command,
        output_dir=str(out_dir),
        wipe_all_flag=False,
        parent=parent,
    )

    assert not commands


def test_overwrite_prompt_continue(monkeypatch, tmp_path):
    src = tmp_path / "a.mkv"
    src.write_text("data")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "a.mkv").write_text("old")

    jobs = [(src, [])]
    commands = []

    def query_tracks(src):
        return []

    def build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=False):
        return ["cmd", str(src), str(dst)]

    def run_command(cmd, capture=True):
        commands.append(cmd)

    exec_instance = DummyExecutor()
    monkeypatch.setattr(processing, "ThreadPoolExecutor", lambda *a, **kw: exec_instance)
    monkeypatch.setattr(processing, "as_completed", dummy_as_completed)
    monkeypatch.setattr(processing.QMessageBox, "question", lambda *a, **k: processing.QMessageBox.Yes)

    parent = type("P", (), {"setEnabled": lambda self, val: None})()
    processing.process_files(
        jobs,
        max_workers=1,
        query_tracks=query_tracks,
        build_cmd=build_cmd,
        run_command=run_command,
        output_dir=str(out_dir),
        wipe_all_flag=False,
        parent=parent,
    )

    assert commands
