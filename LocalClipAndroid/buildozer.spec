# buildozer.spec
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
android.ndk = 25b
android.sdk = 33
android.archs = arm64-v8a
fullscreen = 0