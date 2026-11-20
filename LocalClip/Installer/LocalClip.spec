# LocalClip.spec - PyInstaller build for Windows and macOS (folder build, no console window)
import sys, re

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[('resources/*', 'resources')],
    hiddenimports=['av', 'numpy', 'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets'],
    hookspath=[],
    runtime_hooks=[],
    excludes=['tkinter'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='LocalClip',
    icon='resources/icon.ico' if sys.platform.startswith('win') else 'resources/icon.png',
    debug=False,
    strip=False,
    upx=False,
    console=False,
)

coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=False, name='LocalClip')

# one version for everything: read it from the app itself
try:
    _VERSION = re.search(r'APP_VERSION = "([^"]+)"', open('app/window.py', encoding='utf-8').read()).group(1)
except Exception:
    _VERSION = '0'

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='LocalClip.app',
        icon='resources/icon.png',
        bundle_identifier='org.satdiva.localclip.desktop',
        info_plist={
            'CFBundleName': 'LocalClip',
            'CFBundleDisplayName': 'LocalClip',
            'CFBundleVersion': _VERSION,
            'CFBundleShortVersionString': _VERSION,
            'NSHighResolutionCapable': True,
            'CFBundleDocumentTypes': [{
                'CFBundleTypeName': 'Video',
                'CFBundleTypeRole': 'Viewer',
                'LSItemContentTypes': ['public.movie', 'public.mpeg-4', 'com.apple.quicktime-movie'],
            }],
        },
    )
