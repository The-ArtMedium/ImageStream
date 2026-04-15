[app]

# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain
package.domain = org.satdiva

# (str) TARGETED PATH: Pointing specifically to your app folder
source.dir = ./LocalClipAndroid

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.1.7

# (list) Application requirements
requirements = python3,kivy==2.3.0,ffpyplayer,pillow,hostpython3,openssl

# THE FACE OF THE APP
# Using the source.dir variable to find images inside LocalClipAndroid/
icon.filename = %(source.dir)s/ikon.png
presplash.filename = %(source.dir)s/splash-screen.png

# (str) Supported orientation
orientation = portrait

# (bool) Fullscreen
fullscreen = 0

# (list) Sovereign Permissions
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO

# (int) Android API levels
android.api = 33
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (bool) Accept SDK license
android.accept_sdk_license = True

# (str) Android archs
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
