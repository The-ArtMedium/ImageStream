[app]

# App info
title = LocalClip
package.name = localclip
package.domain = org.imagestream

# Source
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,mp4,txt,ttf,otf

# Version & entry
version = 0.1
entrypoint = main.py

# Stable pinned requirements (this fixes many "no APK" cases)
requirements = python3,kivy==2.3.0

# Display
orientation = portrait
fullscreen = 0

# Android config
android.api = 33
android.minapi = 21
android.archs = arm64-v8a

[buildozer]

# Important for CI
warn_on_root = 1
log_level = 2