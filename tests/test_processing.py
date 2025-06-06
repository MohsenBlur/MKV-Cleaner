import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import types
sys.modules['PySide6'] = types.ModuleType('PySide6')
qtcore = types.ModuleType('PySide6.QtCore')
qtcore.QMetaObject = type('QMetaObject', (), {'invokeMethod': lambda *a, **k: None})
qtcore.Q_ARG = lambda typ, val: val
qtcore.Qt = type('Qt', (), {'WindowModal': 0, 'QueuedConnection': 0})
sys.modules['PySide6.QtCore'] = qtcore

qtwidgets = types.ModuleType('PySide6.QtWidgets')
qtwidgets.QProgressDialog = object
qtwidgets.QMessageBox = type('QMessageBox', (), {
    'warning': staticmethod(lambda *a, **k: None),
    'information': staticmethod(lambda *a, **k: None),
})
sys.modules['PySide6.QtWidgets'] = qtwidgets

import gui.processing as processing  # noqa: E402


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

    def run_command(cmd):
        commands.append(cmd)

    dlg = DummyDialog()

    monkeypatch.setattr(processing, "QProgressDialog", lambda *a, **kw: dlg)
    monkeypatch.setattr(processing, "QMetaObject", type("_", (), {"invokeMethod": lambda *a: a[0].setValue(a[3])}))
    monkeypatch.setattr(processing, "Q_ARG", lambda *a: a[1])
    exec_instance = DummyExecutor()
    monkeypatch.setattr(processing, "ThreadPoolExecutor", lambda *a, **kw: exec_instance)
    monkeypatch.setattr(processing, "as_completed", dummy_as_completed)

    processing.process_files(jobs, max_workers=2, query_tracks=query_tracks,
                             build_cmd=build_cmd, run_command=run_command,
                             output_dir="out", wipe_all_flag=False)

    assert len(commands) == 1
    assert exec_instance.shutdown_called.get("cancel_futures") is True


def test_output_dir_created(monkeypatch, tmp_path):
    jobs = [(tmp_path / "a.mkv", [])]
    commands = []

    def query_tracks(src):
        return []

    def build_cmd(src, dst, tracks, wipe_forced=False, wipe_all=False):
        return ["cmd", str(src), str(dst)]

    def run_command(cmd):
        commands.append(cmd)

    dlg = DummyDialog()

    monkeypatch.setattr(processing, "QProgressDialog", lambda *a, **kw: dlg)
    monkeypatch.setattr(
        processing,
        "QMetaObject",
        type("_", (), {"invokeMethod": lambda *a: a[0].setValue(a[3])}),
    )
    monkeypatch.setattr(processing, "Q_ARG", lambda *a: a[1])
    exec_instance = DummyExecutor()
    monkeypatch.setattr(processing, "ThreadPoolExecutor", lambda *a, **kw: exec_instance)
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
