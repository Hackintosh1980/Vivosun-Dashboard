from setuptools import setup

APP = ['main.py']
DATA_FILES = [
    ('assets', ['assets/Logo.png', 'assets/setup.png'])
]
OPTIONS = {
    'argv_emulation': True,
    'includes': ['tkinter', 'matplotlib', 'numpy', 'pandas', 'vivosun-thermo'],
    'excludes': ['wheel', 'setuptools', 'pkg_resources'],  # verhindert doppelte dist-info
    'iconfile': 'assets/Logo.icns',
    'plist': {
        'CFBundleName': 'VIVOSUN Dashboard',
        'CFBundleDisplayName': 'VIVOSUN Dashboard',
        'CFBundleGetInfoString': "🌱 Vivosun Thermo Dashboard THB-1S",
        'CFBundleIdentifier': 'com.dominik.vivosun-dashboard',
        'CFBundleVersion': '1.2.2',
        'CFBundleShortVersionString': '1.2.2',
    }
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
