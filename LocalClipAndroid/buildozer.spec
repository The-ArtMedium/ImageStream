[app]
# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain (needed for android packaging)
package.domain = org.theartmedium

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let's keep it simple)
source.include_exts = py,png,jpg,kv,atlas

# (list) Application requirements
# Note: ffpyplayer and ffmpeg are the "Heart" of the video engine
requirements = python3,kivy==2.3.0,ffpyplayer,ffmpeg,hostpython3,libffi,openssl,android

# (str) Custom source folders for requirements
# android.add_src = 

# (list) Permissions
# These are the "Keys" to your storage
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO, MANAGE_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
# 33 is required for modern Android video access
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (int) Android SDK version to use
android.sdk = 33

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android entry point, default is ok
# android.entrypoint = org.kivy.android.PythonActivity

# (list) Pattern to whitelist for the whole project
# android.whitelist = 

# (str) Full name including package path of the Java class that implements PythonService
# android.service_class_name = org.kivy.android.PythonService

# (list) Android app themes
# android.theme = @android:style/Theme.NoTitleBar

# (list) Screen orientations
orientation = portrait

# (list) List of service to declare
# services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 1

# (list) Architecture to build for (keep both for compatibility)
android.archs = arm64-v8a, armeabi-v7a

# (bool) allow backup
android.allow_backup = True

# (str) The format used to package the app for release mode (aab or apk)
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk or aar)
android.debug_artifact = apk

[buildozer]
# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = off, 1 = on)
warn_on_root = 1
