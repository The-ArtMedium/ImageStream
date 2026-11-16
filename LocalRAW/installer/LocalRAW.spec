# LocalRAW.spec - PyInstaller build for Windows and macOS (folder build, no console window)
import sys

a = Analysis(
    ['main.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('resources/style.qss', 'resources'),
        ('resources/translations/*.json', 'resources/translations'),
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

if sys.platform == 'darwin':
    app = BUNDLE(
        coll,
        name='LocalRAW.app',
        bundle_identifier='com.localraw.app',
        info_plist={
            'CFBundleName': 'LocalRAW',
            'CFBundleDisplayName': 'LocalRAW',
            'CFBundleVersion': '1.0.0',
            'CFBundleShortVersionString': '1.0.0',
            'NSHighResolutionCapable': True,
        },
    )
