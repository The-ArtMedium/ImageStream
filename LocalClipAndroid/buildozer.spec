[app]

# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain
package.domain = org.satdiva

# (str) SOURCE IS HERE: Since the .spec is in the same folder as main.py
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning
version = 0.1.7

# (list) Application requirements
requirements = python3,kivy==2.3.0,ffpyplayer,pillow,hostpython3,openssl

# THE FACE OF THE APP
# Pointing to the files in the current directory
icon.filename = %(source.dir)s/Ikon.png
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
