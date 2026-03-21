[app]
title = LocalClip
package.name = localclip
package.domain = org.theartmedium
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.0
requirements = python3,kivy,ffpyplayer
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_VIDEO
android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.allow_backup = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
