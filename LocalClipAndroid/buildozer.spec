[app]
# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain
package.domain = org.satdiva

# (str) Version of your application (REQUIRED)
version = 1.0.0

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Application requirements
# Added 'android' and 'python3' explicitly to ensure permissions work
requirements = python3,kivy==2.3.0,ffmpeg,ffpyplayer,pillow,plyer,android,hostpython3,openssl

# (str) Icon of the application
icon.filename = Ikon.png

# (str) Presplash of the application
presplash.filename = splash-screen.png

# (list) Permissions 
# READ_MEDIA_VIDEO is the specific requirement for API 33+
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO, READ_MEDIA_IMAGES

# (int) Target Android API 
android.api = 33
android.minapi = 21
android.ndk = 25b

# (bool) Use unconventional root for build (needed for CI/CD)
warn_on_root = 0

[buildozer]
log_level = 2
warn_on_root = 0
