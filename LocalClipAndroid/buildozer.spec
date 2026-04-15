[app]
title = LocalClip
package.name = localclip
package.domain = org.satdiva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.7

# The 'ffmpeg' and 'ffpyplayer' are the muscles for the video witness
requirements = python3,kivy==2.3.0,ffmpeg,ffpyplayer,pillow,hostpython3,openssl

# ICON FIX: These lines kill the white border drama
icon.filename = %(source.dir)s/Ikon.png
android.adaptive_icon_background = #000000
android.adaptive_icon_foreground = %(source.dir)s/Ikon.png

presplash.filename = %(source.dir)s/splash-screen.png
orientation = portrait
fullscreen = 0

# SOVEREIGN PERMISSIONS
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

# Necessary for FFmpeg libraries to be bundled correctly
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
