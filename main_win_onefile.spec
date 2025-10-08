# -*- mode: python ; coding: utf-8 -*-

import sys, os
sys.path.insert(0, os.path.abspath("."))
import config

block_cipher = None

# --- Analysephase: was alles reinkommt ---
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

# --- Python-Archiv ---
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# --- Executable (eine Datei) ---
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VIVOSUN_Dashboard",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon="assets/icon.ico",
)

# --- Sammelphase (wird bei onefile trotzdem gebraucht!) ---
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name="VIVOSUN_Dashboard"
)

# --- Endgültige OneFile-Build ---
app = BUNDLE(
    coll,
    name="VIVOSUN_Dashboard.exe",
    icon="assets/icon.ico",
    bundle_identifier=None,
    onefile=True,                 # <- entscheidend
    runtime_tmpdir=None,          # entpackt in TEMP
)