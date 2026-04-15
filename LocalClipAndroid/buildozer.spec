[app]
title = LocalClip
package.name = localclip
package.domain = org.satdiva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.7

# Engine Requirements - Balanced for FFmpeg/ffpyplayer stability
requirements = python3,kivy,ffmpeg,ffpyplayer,pillow,hostpython3,openssl

# --- ICON FIX: BIG SCISSORS, NO WHITE BORDER ---
icon.filename = %(source.dir)s/Ikon.png
# This fills the "Safe Zone" background with Black
android.adaptive_icon_background = #000000
# This places the cropped scissors on top
android.adaptive_icon_foreground = %(source.dir)s/Ikon.png

presplash.filename = %(source.dir)s/splash-screen.png
orientation = portrait
fullscreen = 0

# PERMISSIONS
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

# Necessary to package the FFmpeg "muscles"
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
