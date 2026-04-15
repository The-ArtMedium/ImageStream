[app]

# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain (needed for android packaging)
package.domain = org.satdiva

# (str) Source code where the main.py lives
source.dir = .

# (list) Source files to include (let's keep it tight)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.1.7

# ADD 'plyer' HERE. Without it, the "Select" button is a dead end.
requirements = python3,kivy,ffmpeg,ffpyplayer,pillow,plyer,hostpython3,openssl

# --- THE ICON TRANSFORMATION ---
# This is the base icon for older systems
icon.filename = %(source.dir)s/Ikon.png

# ADAPTIVE ICON PROTOCOL: This is how we kill the white border.
# 1. Background: Forces the "frame" to be solid black
android.adaptive_icon_background = #000000
# 2. Foreground: Places your scissors on top of the black
android.adaptive_icon_foreground = %(source.dir)s/Ikon.png

# (str) Presplash of the application
presplash.filename = %(source.dir)s/splash-screen.png

# (str) Supported orientation
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# We need these to witness the equestrian and world cup archives
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then skip trying to update the libs
android.skip_update = False

# (bool) If True, then automatically accept SDK license
android.accept_sdk_license = True

# (str) The Android arch to build for
android.archs = arm64-v8a

# CRITICAL: This bundles the FFmpeg libraries so the trimmer doesn't shut down
android.copy_libs = 1

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
