[buildozer]
warn_on_root = 1

[app]
source.dir = .
title = LocalClip
package.name = localclip
package.domain = org.imagestream
source.include_exts = py,png,jpg,kv,mp4,txt
version = 0.1
entrypoint = main.py
requirements = python3,kivy
orientation = portrait
android.api = 33
android.minapi = 21
android.ndk_api = 21
android.archs = arm64-v8a
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.3.13750724
android.sdk_path = /usr/local/lib/android/sdk
fullscreen = 0