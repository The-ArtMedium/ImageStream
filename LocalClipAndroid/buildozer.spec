[app]
title = LocalClip
package.name = localclip
package.domain = org.satdiva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.7

# KEEP THIS ORDER
requirements = python3,kivy==2.3.0,ffmpeg,ffpyplayer,pillow,hostpython3,openssl

# ICON FIX: Force the foreground to be your logo and the background to be black
# This removes the white "legacy" border that makes the icon look small
icon.filename = %(source.dir)s/Ikon.png
android.adaptive_icon_background = #000000
android.adaptive_icon_foreground = %(source.dir)s/Ikon.png

presplash.filename = %(source.dir)s/splash-screen.png
orientation = portrait
fullscreen = 0

# SOVEREIGN PERMISSIONS
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO

android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

# CRITICAL: THIS IS THE FIX FOR THE SHUT-OFF
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
