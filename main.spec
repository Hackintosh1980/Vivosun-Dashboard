# -*- mode: python ; coding: utf-8 -*-

import sys, os
from PyInstaller.utils.hooks import collect_submodules

# --- Version und App-Infos aus config.py ---
sys.path.insert(0, os.path.abspath("."))   # Projektpfad hinzufügen
import config

block_cipher = None

a = Analysis(
    ['main.py'],                      # Einstiegspunkt
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets/*', 'assets'),        # Icons & PNGs
        ('config.json', '.'),          # Konfiguration
        ('status.json', '.'),          # Status
        ('thermo_history.csv', '.'),   # Historie
    ],
    hiddenimports=(
        collect_submodules('matplotlib')
        + collect_submodules('tkinter')
        + collect_submodules('vivosun_thermo')
    ),
    hookspath=[],
    runtime_hooks=[],
    excludes=[
        # --- Schwergewichte, die wir definitiv nicht brauchen ---
        'torch', 'torchvision', 'torchaudio', 'ultralytics',
        'tensorflow', 'cv2', 'onnx', 'openvino',
        'sklearn',

        # --- scipy + Submodule (wird von pandas/matplotlib getriggert) ---
        'scipy', 'scipy.spatial', 'scipy.linalg',
        'scipy.special', 'scipy.stats'
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
    console=False,   # True = mit Terminalfenster starten; False = nur App
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='VIVOSUN_Dashboard'
)

app = BUNDLE(
    coll,
    name='VIVOSUN_Dashboard.app',
    icon='assets/logo.icns',
    bundle_identifier='com.cueva.vivosun',
    info_plist={
        "CFBundleName": config.APP_NAME,
        "CFBundleDisplayName": config.APP_NAME,
        "CFBundleGetInfoString": f"{config.APP_NAME} by {config.APP_AUTHOR}",
        "CFBundleShortVersionString": config.APP_VERSION,
        "CFBundleVersion": config.APP_VERSION,
        "NSHumanReadableCopyright": f"© 2025 {config.APP_AUTHOR}",
        "NSHighResolutionCapable": True,
        "LSMultipleInstancesProhibited": True,
        "LSUIElement": False,
    },
)