import shutil
import sys
from PyInstaller.utils.hooks import collect_submodules

binaries = []
for exe in ("mkvmerge", "mkvextract", "ffmpeg", "ffprobe"):
    path = shutil.which(exe)
    if path:
        binaries.append((path, '.'))

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
