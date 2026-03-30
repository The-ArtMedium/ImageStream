r[app]

title = LocalClip
package.name = localclip
package.domain = org.localclip

source.dir = .
source.include_exts = py,kv,mp4,mkv,mov,avi,webm,m4v

version = 0.1
orientation = portrait
fullscreen = 0

# ---- Requirements ----
requirements = python3, kivy==2.2.1, ffpyplayer, cython==0.29.37

# ---- Android API / NDK ----
android.api = 33
android.minapi = 21
android.ndk = 27.0.12077973
android.archs = arm64-v8a, armeabi-v7a

# ---- Permissions (Android 13+) ----
android.permissions = READ_MEDIA_VIDEO, READ_MEDIA_IMAGES, READ_MEDIA_AUDIO

# ---- Bootstrap ----
android.bootstrap = sdl2

# ---- Storage / File Access ----
android.allow_backup = True
android.allow_cleartext_traffic = True

# ---- Icons (optional) ----
# icon.filename = icons/icon.png
# presplash.filename = icons/splash.png

# ---- Log Level ----
log_level = 2

# ---- Keep Buildozer Clean ----
p4a.local_recipes = ./p4a-recipes

android.sdk_path = /usr/local/lib/android/sdk
android.ndk_path = /usr/local/lib/android/sdk/ndk/27.0.12077973