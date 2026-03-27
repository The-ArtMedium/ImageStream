[app]
# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain
package.domain = org.theartmedium

# (str) Version of your application (CRITICAL FIX)
version = 0.1

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# Including the video engine components
requirements = python3,kivy==2.3.0,ffpyplayer,ffmpeg,hostpython3,libffi,openssl,android

# (list) Permissions (The Keys to the Vault)
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO, MANAGE_EXTERNAL_STORAGE

# (int) Target Android API (33 is required for modern video access)
android.api = 33

# (int) Minimum API your APK will support
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use private data storage
android.private_storage = True

# (list) Screen orientations
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Architecture to build for
android.archs = arm64-v8a, armeabi-v7a

# (str) The format used to package the app
android.release_artifact = apk
android.debug_artifact = apk

[buildozer]
# (int) Log level (2 = debug)
log_level = 2
warn_on_root = 1
