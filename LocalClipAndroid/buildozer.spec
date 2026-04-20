[app]
# ... all your existing settings ...

# Force p4a to install requirements
p4a.hook =

title = LocalClip
package.name = localclip
package.domain = org.satdiva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.0

presplash.filename = splash-screen.png
icon.filename = Ikon.png

requirements = python3,kivy==2.3.0,kvdroid,pillow,plyer,android

orientation = portrait
fullscreen = 1

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,android.permission.READ_MEDIA_VIDEO

android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.enable_androidx = True
android.archs = arm64-v8a,armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1