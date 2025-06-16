# app.spec
# -*- mode: python ; coding: utf-8 -*-

import os
from PyInstaller.utils.hooks import collect_submodules

# Use the working directory where you run PyInstaller
project_path = os.getcwd()

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[project_path],
    binaries=[],
    datas=[
        # Include your JSON and any other data folders
        ('data', 'data'),
        (os.path.join(project_path, 'userSettings.json'), '.'),
        (os.path.join(project_path, 'assets'), 'assets'),
    ],
    hiddenimports=(
        collect_submodules('controller') +
        collect_submodules('gui') +
        collect_submodules('helper') +
        collect_submodules('data_visualization')
    ),
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='StabilityApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,            # False → no console window
    icon=None,               # Or 'assets/logo.ico' if you have an icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='StabilityApp'
)
