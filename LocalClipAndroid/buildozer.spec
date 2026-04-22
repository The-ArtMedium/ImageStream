# buildozer.spec — LocalClip
# Frame scrubbing + lossless ffmpeg clip
# No ExoPlayer, no AAR, no gradle dependencies

[app]
title = LocalClip
package.name = localclip
package.domain = org.satdiva

source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# IMPORTANT: include the ffmpeg binary in the APK
# Place your arm64 ffmpeg binary at: ./bin/ffmpeg
# Download from: https://github.com/eugeneware/ffmpeg-static
# or ffmpeg-kit Android release (ffmpeg binary only, ~8MB arm64)
source.include_patterns = bin/ffmpeg,splash-screen.png,Ikon.png

version = 0.1.0

presplash.filename = splash-screen.png
icon.filename = Ikon.png

# pyjnius is required for MediaMetadataRetriever
requirements = python3,kivy==2.3.0,pillow,plyer,android,pyjnius

orientation = portrait
fullscreen = 1

android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,android.permission.READ_MEDIA_VIDEO

android.api = 33
android.minapi = 26
# minapi 26 required for OPTION_CLOSEST (frame-accurate seek)
# If you need minapi 21, change OPTION_CLOSEST (2) to OPTION_CLOSEST_SYNC (3) in main.py
# OPTION_CLOSEST_SYNC seeks to nearest keyframe instead — still works, less precise

android.ndk = 25b
android.sdk = 33
android.enable_androidx = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
