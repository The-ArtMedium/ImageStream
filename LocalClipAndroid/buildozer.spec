[app]
title = LocalClip
package.name = localclip
package.domain = org.theartmedium

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1.0

# Added ffmpeg, openssl, and libffi for secure, lossless processing
requirements = python3,kivy==2.3.0,ffpyplayer,ffmpeg,hostpython3,libffi,openssl

orientation = portrait
fullscreen = 0

# Updated for modern Android API 33 storage rules
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO, MANAGE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a
android.accept_sdk_license = True

# Removed the hardcoded sdk_path and ndk_path to let GitHub Actions handle it

[buildozer]
log_level = 2
warn_on_root = 1
