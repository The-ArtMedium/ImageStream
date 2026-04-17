[app]
title = LocalClip
package.name = localclip
package.domain = org.satdiva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.0

presplash.filename = Splash-screen.png
icon.filename = Ikon.png

requirements = python3,kivy==2.3.0,ffmpeg,ffpyplayer,pillow,plyer,android,hostpython3,openssl

orientation = portrait
fullscreen = 1

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,android.permission.READ_MEDIA_VIDEO

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

[buildozer]
log_level = 2
warn_on_root = 1