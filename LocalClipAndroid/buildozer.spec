[buildozer]
# Section required by Buildozer to avoid NoSectionError
warn_on_root = 1

[app]
# (str) Source code where your main.py lives
source.dir = .

# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain (reverse DNS style)
package.domain = org.imagestream

# (list) Source files to include
source.include_exts = py,png,jpg,kv,mp4,txt

# (str) Application version
version = 0.1

# (str) Entry point / main Python file
entrypoint = main.py

# (list) Requirements (Python modules to include)
requirements = python3,kivy

# (str) Orientation
orientation = portrait

# (int) Android API to target
android.api = 33

# (int) Minimum Android API
android.minapi = 21

# (str) Android NDK version
android.ndk = 25b

# (str) Android SDK version
android.sdk = 33

# (bool) Fullscreen
fullscreen = 0

# (str) Presplash image (optional)
# presplash.filename = %(source.dir)s/data/presplash.png
