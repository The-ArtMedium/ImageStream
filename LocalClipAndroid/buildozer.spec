[app]
title = LocalClip
package.name = localclip
package.domain = org.satdiva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.0

# Assets
presplash.filename = Splash-screen.png
icon.filename = Ikon.png

# Full requirement list for local-first video processing
requirements = python3,kivy==2.3.0,ffmpeg,ffpyplayer,pillow,plyer,android,hostpython3,openssl

orientation = portrait
fullscreen = 1

# Permissions — covers Android 10, 12, and 13+
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,android.permission.READ_MEDIA_VIDEO

android.api = 33
android.minapi = 21

# FIX #9: pinned NDK prevents inconsistent builds across environments
android.ndk = 25b
android.sdk = 33

[buildozer]
log_level = 2
warn_on_root = 1

