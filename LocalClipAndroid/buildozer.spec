[app]

# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain (needed for android packaging)
package.domain = org.satdiva

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (including your branding assets)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.1.7

# (list) Application requirements
# ffpyplayer is the engine that actually "witnesses" the video pixels
requirements = python3,kivy==2.3.0,ffpyplayer,pillow,hostpython3,openssl

# THE FACE OF THE APP
# These names must match your uploaded files exactly
icon.filename = %(source.dir)s/ikon.png
presplash.filename = %(source.dir)s/splash-screen.png

# (str) Supported orientation (set to portrait for your new layout)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# MANAGE_EXTERNAL_STORAGE is the "Golden Key" for Android 11+ to save files
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO

# (int) Target Android API (API 33 is standard for 2026)
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (bool) Automatically accept SDK license
android.accept_sdk_license = True

# (str) The Android arch to build for
android.archs = arm64-v8a

[buildozer]

# (int) Log level (2 = debug, which is best for finding why things "grey out")
log_level = 2

# (int) Display warning if buildozer is run as root
warn_on_root = 1
