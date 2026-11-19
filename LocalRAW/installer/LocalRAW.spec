# LocalRAW.spec - PyInstaller build for Windows and macOS (folder build, no console window)
import sys

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('resources/style.qss', 'resources'),
        ('resources/translations/*.json', 'resources/translations'),
        ('resources/models/*', 'resources/models'),          # the small offline face finder
    ],
    hiddenimports=['rawpy', 'cv2', 'numpy', 'PIL', 'piexif'],
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LocalRAW',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='LocalRAW',
)

# one version for everything: read it from the app itself
import re as _re
try:
    _VERSION = _re.search(r'APP_VERSION = "([^"]+)"', open('app/ui/main_window.py', encoding='utf-8').read()).group(1)
except Exception:
    _VERSION = '0'

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='LocalRAW.app',
        bundle_identifier='com.localraw.app',
        info_plist={
            'CFBundleName': 'LocalRAW',
            'CFBundleDisplayName': 'LocalRAW',
            'CFBundleVersion': _VERSION,
            'CFBundleShortVersionString': _VERSION,
            'NSHighResolutionCapable': True,
        },
    )
