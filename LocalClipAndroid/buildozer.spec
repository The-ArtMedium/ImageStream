[app]
title = LocalClip
package.name = localclip
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.2
requirements = python3,kivy==2.3.0,ffpyplayer,pyjnius
orientation = portrait
fullscreen = 0

# Permissions
android.permissions = READ_MEDIA_VIDEO, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE

# Bundle ffmpeg
android.add_ffmpeg = True
android.api = 31
android.minapi = 21

# Buildozer settings
[buildozer]
log_level = 2
warn_on_root = 1
android.accept_sdk_license = True