# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

datas = [
    ('config', 'config'),
    ('core', 'core'),
    ('gui', 'gui'),
    ('utils', 'utils'),
    ('geoip.dat', '.'),
    ('geosite.dat', '.'),
    ('xray.exe', '.'),
    ('wxray.exe', '.'),
    ('README.md', '.'),
    ('LICENSE', '.')
]

if os.path.exists('.env'):
    datas.append(('.env', '.'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PyQt6',
        'aiohttp',
        'psutil',
        'requests',
        'dotenv',
        'rich',
        'yaml',
        'telegram',
        'geoip2'
    ],
    hookspath=[],
    hooksconfig={},
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
    name='VlessParser',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
