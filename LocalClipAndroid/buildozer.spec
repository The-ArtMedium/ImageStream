[app]
title = LocalClip
package.name = localclip
package.domain = org.satdiva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.7

# Engine Requirements
requirements = python3,kivy==2.3.0,ffmpeg,ffpyplayer,pillow,hostpython3,openssl

# --- THE "REAL ICON" PROTOCOL ---
# 1. Base icon for old systems
icon.filename = %(source.dir)s/Ikon.png

# 2. Adaptive Background (Solid Black to kill all borders)
android.adaptive_icon_background = #000000

# 3. Adaptive Foreground (This is what makes it "Big")
# Note: If Ikon.png is cropped tight to the edges, it will fill the icon perfectly.
android.adaptive_icon_foreground = %(source.dir)s/Ikon.png

# --- OPERATIONAL SETTINGS ---
presplash.filename = %(source.dir)s/splash-screen.png
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a
android.copy_libs = 1

[buildozer]
log_level = 2
warn_on_root = 1
