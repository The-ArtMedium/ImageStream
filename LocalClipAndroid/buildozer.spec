[app]
title = LocalClip
package.name = localclip
package.domain = org.satdiva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.3

# THE FINAL ENGINE REQUIREMENTS
requirements = python3, kivy==2.3.0, ffpyplayer, ffmpeg, pyjnius, android

orientation = landscape
fullscreen = 1

# Permissions for API 33+
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO

# ARCHITECTURE & API
android.archs = arm64-v8a
android.api = 33
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True

# Necessary for storage access on modern Android
android.manifest.request_legacy_external_storage = true

[buildozer]
log_level = 2
warn_on_root = 1
