[app]
title = LocalClip
package.name = localclip
package.domain = org.satdiva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.0

# Ensure these EXACT names exist in your root folder
presplash.filename = splash-screen.png
icon.filename = Ikon.png

# NO ffpyplayer. NO kvdroid. NO exoplayer. Just Kivy and Android.
requirements = python3,kivy==2.3.0,pillow,android

android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, android.permission.READ_MEDIA_VIDEO
android.api = 33
android.minapi = 21
android.ndk = 25b
android.enable_androidx = True
android.archs = arm64-v8a, armeabi-v7a
