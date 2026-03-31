[app]

title = LocalClip
package.name = localclip
package.domain = org.localclip
source.dir = .
source.include_exts = py,kv,png,jpg,mp4,txt,md
version = 1.0.0
requirements = python3,kivy,kivymd,ffpyplayer
orientation = portrait
fullscreen = 0
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE,INTERNET
android.api = 35
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.allow_backup = True
android.debug_obfuscate = False
android.enable_androidx = True
android.gradle_dependencies = androidx.core:core-ktx:1.12.0

# --- CRITICAL MODERN SDK PATHS ---
android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/25.2.9519653
android.android_home = /usr/local/lib/android/sdk
android.sdkmanager_path = /usr/local/lib/android/sdk/cmdline-tools/latest/bin/sdkmanager

# --- BUILD TOOLS ---
android.build_tools_version = 35.0.0

# --- ICONS / SPLASH ---
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

# --- PYTHON OPTIONS ---
python.version = 3
python.code = main.py

# --- LOGGING ---
log_level = 2

# --- PACKAGING ---
package.format = apk

# --- MISC ---
android.accept_sdk_license = True
p4a.local_recipes = ./recipes