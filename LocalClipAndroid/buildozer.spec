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
requirements = python3==3.11.6, kivy==2.2.1

orientation = portrait
fullscreen = 0

# Android config
android.api = 35
android.minapi = 21
android.ndk = 25.2.9519653
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653
android.sdk_path = /usr/local/lib/android/sdk
android.archs = arm64-v8a, armeabi-v7a
android.build_tools = 35.0.0

# Permissions
android.permissions = CAMERA, RECORD_AUDIO, READ_MEDIA_VIDEO, READ_MEDIA_IMAGES, READ_MEDIA_AUDIO

# GitHub Actions
android.accept_sdk_license = True

# Entry point
entrypoint = main.py

# Lock p4a to a stable version
p4a.branch = v2024.06.01