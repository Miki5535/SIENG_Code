# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\\\Users\\\\65011\\\\Desktop\\\\Segano\\\\work00002\\\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\\\Users\\\\65011\\\\Desktop\\\\Segano\\\\work00002\\\\audioexample', 'audioexample'), ('C:\\\\Users\\\\65011\\\\Desktop\\\\Segano\\\\work00002\\\\photoexample', 'photoexample'), ('C:\\\\Users\\\\65011\\\\Desktop\\\\Segano\\\\work00002\\\\tabs', 'tabs'), ('C:\\\\Users\\\\65011\\\\Desktop\\\\Segano\\\\work00002\\\\utils', 'utils'), ('C:\\\\Users\\\\65011\\\\Desktop\\\\Segano\\\\work00002\\\\vdio', 'vdio'), ('C:\\\\Users\\\\65011\\\\Desktop\\\\Segano\\\\work00002\\\\icom.png', '.'), ('C:\\\\Users\\\\65011\\\\Desktop\\\\Segano\\\\work00002\\\\myicon_in.ico', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\65011\\Desktop\\Segano\\work00002\\myicon.ico'],
)
