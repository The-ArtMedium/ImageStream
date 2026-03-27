[app]
# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip
package.domain = org.theartmedium
version = 0.1
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# --- THE NERVE CENTER (Requirements) ---
# FIXED: Added plyer (Gallery), ffpyplayer (Video), and jnius (Android bridge)
requirements = python3, kivy==2.3.0, ffpyplayer, plyer, sdl2, pysdl2, android, jnius, hostpython3, libffi, openssl

# --- THE KEYS TO THE VAULT (Permissions) ---
# FIXED: Added specific media access for Android 13+ (API 33)
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO

# --- THE ENGINE SPECS ---
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.private_storage = True
orientation = portrait
fullscreen = 1
android.archs = arm64-v8a, armeabi-v7a
android.release_artifact = apk
android.debug_artifact = apk

[buildozer]
log_level = 2
warn_on_root = 1
