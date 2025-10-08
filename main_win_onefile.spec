# -*- mode: python ; coding: utf-8 -*-

import sys, os
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
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- ONEFILE EXE ---
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
    console=False,              # kein Terminalfenster
    icon='assets/icon.ico',
    onefile=True,               # <- wichtig: alles in einer Datei
    runtime_tmpdir=None,        # entpackt automatisch im Temp-Verzeichnis
)