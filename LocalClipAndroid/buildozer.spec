[app]

# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain
package.domain = org.satdiva

# (str) Version of your application (REQUIRED)
version = 1.0.0

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Application requirements
requirements = python3,kivy==2.3.0,ffmpeg,ffpyplayer,pillow,plyer,hostpython3,openssl

# (str) Icon of the application
icon.filename = icon.png

# (str) Presplash of the application
presplash.filename = splash.png

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API
android.api = 33
android.minapi = 21
android.ndk = 25b

# (bool) Use unconventional root for build (needed for CI/CD)
warn_on_root = 0

[buildozer]
log_level = 2
warn_on_root = 0
