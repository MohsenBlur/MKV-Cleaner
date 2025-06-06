import shutil
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

binaries = []
for exe in ("ffmpeg", "ffprobe"):
    path = shutil.which(exe)
    if not path:
        raise RuntimeError(f"Required executable '{exe}' not found on PATH")
    binaries.append((path, '.'))

# On Windows we also need the DLLs shipped with ffprobe
if sys.platform == "win32":
    ffprobe_path = shutil.which("ffprobe")
    if ffprobe_path:
        base = Path(ffprobe_path).resolve().parent
        search_dirs = [base]
        bin_dir = base / "bin"
        if bin_dir.is_dir():
            search_dirs.append(bin_dir)
        for directory in search_dirs:
            for dll in directory.rglob("*.dll"):
                binaries.append((str(dll), '.'))

hidden = collect_submodules('gui') + collect_submodules('core')

block_cipher = None


a = Analysis(
    ['mkv_cleaner.py'],
    pathex=[],
    binaries=binaries,
    datas=[],
    hiddenimports=hidden,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='mkv-cleaner',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
)
