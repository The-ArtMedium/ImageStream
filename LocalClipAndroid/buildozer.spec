[app]

# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain (usually reverse domain style)
package.domain = org.imagestream

# (str) Source code directory (relative to this .spec)
source.dir = .

# (list) Source files to include (space or comma separated)
source.include_exts = py,png,jpg,jpeg,kv,mp4,txt,ttf,otf

# (str) Application version
version = 0.1

# (str) Python main file
entrypoint = main.py

# (list) Application requirements - pinned for better compatibility on CI
requirements = python3,kivy==2.3.0

# (str) Orientation of the app
orientation = portrait

# (int) Android API level
android.api = 33
android.minapi = 21

# (str) Android architecture(s) to build for
android.archs = arm64-v8a

# (bool) Fullscreen
fullscreen = 0

# Optional: Add more libraries here later if needed (uncomment and adjust)
# requirements = python3,kivy==2.3.0,kivymd,pillow

# Remove or keep commented - these often cause path conflicts on GitHub Actions
# android.ndk_path = ...
# android.sdk_path = ...

[buildozer]
# Important settings for CI
warn_on_root = 1
log_level = 2

# Optional: Force a specific python-for-android branch if needed later
# p4a.branch = master