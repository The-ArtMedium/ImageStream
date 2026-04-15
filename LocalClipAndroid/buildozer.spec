[app]

# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain
package.domain = org.satdiva

# (str) Source code where main.py lives
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.1.7

# (list) Application requirements
# ffmpeg and ffpyplayer are the "eyes" required to witness the video pixels
requirements = python3,kivy==2.3.0,ffmpeg,ffpyplayer,pillow,hostpython3,openssl

# THE FACE OF THE APP
# Pointing to your branded assets in the same folder
icon.filename = %(source.dir)s/Ikon.png
presplash.filename = %(source.dir)s/splash-screen.png

# ADAPTIVE ICON FIX
# This fills the white border with black to make your logo look full-sized
android.adaptive_icon_background = #000000
android.adaptive_icon_foreground = %(source.dir)s/Ikon.png

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (list) Sovereign Permissions
# Keys to accessing the drive footage and media folders
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO

# (int) Android API levels
android.api = 33
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) The Android architecture (Required for modern devices)
android.archs = arm64-v8a

[buildozer]
# (int) Log level (2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (1 = enabled)
warn_on_root = 1
