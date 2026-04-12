[app]
title = LocalClip
package.name = localclip
package.domain = org.imagestream

source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,mp4,txt,ttf,otf

version = 0.1
entrypoint = main.py

# ⚠️ keep minimal + stable first
requirements = python3,kivy==2.3.0,ffpyplayer

orientation = portrait
fullscreen = 0

# Android settings
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.ndk = 25b
android.ndk_api = 21


[buildozer]
warn_on_root = 1
log_level = 2

# IMPORTANT: forces newer python-for-android (fixes ffpyplayer Cython mismatch)
p4a.branch = master