[app]
title = LocalClip
package.name = localclip
package.domain = org.theartmedium

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

version = 0.1.0

requirements = python3,kivy==2.2.1,ffpyplayer,hostpython3

orientation = portrait
fullscreen = 0

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_VIDEO
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.allow_backup = True
android.archs = arm64-v8a
android.build_tools_version = 33.0.2
android.accept_sdk_license = True
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.1.8937393

[buildozer]
log_level = 2
warn_on_root = 1