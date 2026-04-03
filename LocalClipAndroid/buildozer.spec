[app]

# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain (usually reverse domain style)
package.domain = org.imagestream

# (str) Source code directory (relative to this .spec)
source.dir = .

# (list) Source files to include (space or comma separated)
source.include_exts = py,png,jpg,jpeg,kv,mp4,txt,ttf,otf

# (str) Application version
version = 0.1

# (str) Python main file
entrypoint = main.py

# (list) Application requirements
# Use older Cython for stability with Kivy on Android
requirements = python3,kivy

# (str) Orientation of the app
orientation = portrait

# (int) Android API level
android.api = 33
android.minapi = 21

# (str) Android architecture(s) to build for
android.archs = arm64-v8a

# (bool) Fullscreen
fullscreen = 0

# Optional: If you later add more libs (e.g. kivymd, pillow, etc.)
# requirements = python3,kivy,kivymd,pillow

# Remove or comment these if they were causing conflicts:
# android.ndk_path = ...
# android.sdk_path = ...

[buildozer]
warn_on_root = 1