# -*- mode: python ; coding: utf-8 -*-

import sys, os

# --- Version und App-Infos aus config.py ---
sys.path.insert(0, os.path.abspath("."))
import config

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),
        ('config.json', '.'),
        ('status.json', '.'),
        ('thermo_history.csv', '.'),
    ],
    hiddenimports=[
        "matplotlib.backends.backend_tkagg",
        "matplotlib.pyplot",
        "matplotlib.dates",
        "matplotlib.patheffects",
        "tkinter",
        "numpy",
        "PIL",
        "pandas",
        "vivosun_thermo",
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        "matplotlib.tests",
        "mpl_toolkits.tests",
        "tkinter.test",
        "scipy",
        "torch",
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VIVOSUN_Dashboard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,                   # Kein Terminal
    icon='assets/icon.ico',          # Windows-Icon
    onefile=True,                    # <== Hier der Schlüssel: eine einzige .exe
    runtime_tmpdir=None,             # entpackt sich im Temp
    append_pkg=False,                # alles intern in der EXE
)