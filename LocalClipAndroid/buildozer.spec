[app]
title = LocalClip
package.name = localclip
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.2

# THE CORRECT MANIFEST
requirements = python3, kivy==2.3.0, ffpyplayer, ffmpeg, pyjnius, android

orientation = landscape
fullscreen = 0

# Permissions for API 31+
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# ARCHITECTURE (Stick to one to avoid memory crashes in Actions)
android.archs = arm64-v8a

# API SETTINGS
android.api = 33
android.minapi = 21
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
