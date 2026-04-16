[app]
title = LocalClip
package.name = localclip
package.domain = org.imagestream
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,mp4,txt,ttf,otf
version = 0.1
entrypoint = main.py
requirements = python3,kivy==2.3.0,ffpyplayer
orientation = portrait
fullscreen = 0
android.api = 33
android.minapi = 21
android.archs = arm64-v8a
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE,READ_MEDIA_VIDEO

[buildozer]
warn_on_root = 1
log_level = 2