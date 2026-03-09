import PyInstaller.__main__

PyInstaller.__main__.run([
    'app/main.py',
    '--name=LocalRAW',
    '--onefile',
    '--windowed',
])