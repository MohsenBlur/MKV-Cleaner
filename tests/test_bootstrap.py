import builtins
import os
import shutil
import sys
import zipfile
from pathlib import Path
import importlib

import core.bootstrap as bootstrap


def test_ensure_binary_download(monkeypatch, tmp_path):
    monkeypatch.delenv('MKVCLEANER_SKIP_BOOTSTRAP', raising=False)
    monkeypatch.setattr(bootstrap, 'SKIP_BOOTSTRAP', None)
    exe = 'tool.exe' if os.name == 'nt' else 'tool'
    archive = tmp_path / 'a.zip'
    with zipfile.ZipFile(archive, 'w') as z:
        z.writestr(exe, 'x')

    calls = []

    def fake_urlretrieve(url, filename):
        shutil.copy(archive, filename)
        calls.append(url)

    monkeypatch.setattr(bootstrap, 'APP_DIR', tmp_path)
    monkeypatch.setattr(bootstrap.urllib.request, 'urlretrieve', fake_urlretrieve)

    path = bootstrap.ensure_binary(exe, 'http://example/archive.zip')
    assert Path(path) == tmp_path / exe
    assert (tmp_path / exe).exists()
    assert calls

    calls.clear()
    bootstrap.ensure_binary(exe, 'http://example/archive.zip')
    assert not calls


def test_ensure_python_package(monkeypatch):
    monkeypatch.delenv('MKVCLEANER_SKIP_BOOTSTRAP', raising=False)
    monkeypatch.setattr(bootstrap, 'SKIP_BOOTSTRAP', None)
    orig_import = builtins.__import__

    def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
        if name == 'somepkg':
            raise ImportError
        return orig_import(name, globals, locals, fromlist, level)

    called = {}

    def fake_run(cmd, check):
        called['cmd'] = cmd
        called['check'] = check

    monkeypatch.setattr(builtins, '__import__', fake_import)
    monkeypatch.setattr(bootstrap.subprocess, 'run', fake_run)

    bootstrap.ensure_python_package('somepkg')
    assert called['cmd'][0] == sys.executable


def test_config_uses_system_binaries(monkeypatch):
    import importlib
    import core.config as config

    called = []
    monkeypatch.setattr(bootstrap, 'ensure_binary', lambda exe, url: called.append(True))

    importlib.reload(config)
    ext = '.exe' if os.name == 'nt' else ''
    assert config.MKVMERGE == f'mkvmerge{ext}'
    assert config.DEFAULTS['mkvmerge_cmd'] == f'mkvmerge{ext}'
    assert config.DEFAULTS['ffmpeg_cmd'] == f'ffmpeg{ext}'
    assert not called


def test_skip_ensure_binary(monkeypatch, tmp_path):
    exe = 'tool.exe' if os.name == 'nt' else 'tool'
    monkeypatch.setattr(bootstrap, 'APP_DIR', tmp_path)
    monkeypatch.setattr(bootstrap, 'SKIP_BOOTSTRAP', '1')

    called = []

    def fake_urlretrieve(url, filename):
        called.append(True)

    monkeypatch.setattr(bootstrap.urllib.request, 'urlretrieve', fake_urlretrieve)
    monkeypatch.setenv('MKVCLEANER_SKIP_BOOTSTRAP', '1')

    path = bootstrap.ensure_binary(exe, 'http://example/archive.zip')
    assert Path(path) == tmp_path / exe
    assert not called


def test_skip_ensure_python_package(monkeypatch):
    monkeypatch.setattr(bootstrap, 'SKIP_BOOTSTRAP', '1')
    monkeypatch.setenv('MKVCLEANER_SKIP_BOOTSTRAP', '1')
    called = {}

    def fake_run(cmd, check):
        called['run'] = True

    monkeypatch.setattr(bootstrap.subprocess, 'run', fake_run)

    bootstrap.ensure_python_package('somepkg')
    assert 'run' not in called

