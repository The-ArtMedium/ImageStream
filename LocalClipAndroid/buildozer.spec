[app]
title = LocalClip
package.name = localclip
package.domain = org.theartmedium
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.0

# The Engine (ffmpeg is the key for lossless video)
requirements = python3,kivy==2.3.0,ffpyplayer,ffmpeg,hostpython3,libffi,openssl

orientation = portrait
fullscreen = 0

# The Sovereign Keys (Storage access for Android 13+)
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO, READ_MEDIA_IMAGES, READ_MEDIA_AUDIO
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

android.accept_sdk_license = True
android.skip_update = False

[buildozer]
log_level = 2
warn_on_root = 1
