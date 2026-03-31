[buildozer]
warn_on_root = 0
log_level = 2

[app]
title = LocalClip
package.name = localclip
package.domain = org.localclip
source.dir = .
source.include_exts = py,png,jpg,kv,mp4,txt,md
version = 0.1
requirements = python3,kivy
orientation = portrait
fullscreen = 0

android.api = 35
android.minapi = 21
android.sdk = 35
android.ndk = 25b
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653
android.sdk_path = /usr/local/lib/android/sdk
android.archs = arm64-v8a,armeabi-v7a
android.build_tools = 35.0.0

# Permissions
android.permissions = CAMERA, RECORD_AUDIO, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# Keep this ON for GitHub Actions
android.accept_sdk_license = True

# Icon (optional)
# icon.filename = icon.png

# Entry point
entrypoint = main.py

# Do not touch
p4a.branch = master