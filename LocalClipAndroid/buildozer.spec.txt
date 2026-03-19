[app]
title = LocalClip
package.name = localclip
package.domain = org.theartmedium
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.0
requirements = python3,kivy,ffpyplayer
orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_MEDIA_VIDEO
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21
android.allow_backup = True
android.arch = arm64-v8a

# ffmpeg bundled for lossless export
android.add_jars =
android.add_libs_armeabi_v7a =

[buildozer]
log_level = 2
warn_on_root = 1
