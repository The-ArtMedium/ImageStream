[app]

# (str) Title of your application
title = LocalClip

# (str) Package name
package.name = localclip

# (str) Package domain (needed for android/ios packaging)
package.domain = org.satdiva

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let's keep it lean)
source.include_exts = py,png,jpg,kv,atlas,json

# (list) Application requirements
requirements = python3,kivy==2.3.0,ffmpeg,ffpyplayer,pillow,plyer,hostpython3,openssl

# (str) Custom source footprint for the "Donation" link or info
# You can reference this in your UI code
metadata.donation_url = https://your-donation-link.com

# (str) Icon of the application
# Ensure 'icon.png' is in your source directory
icon.filename = icon.png

# (str) Presplash of the application (The "Header" / Brief splash)
# Ensure 'splash.png' is in your source directory
presplash.filename = splash.png

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use unconventional root for build (needed for CI/CD)
warn_on_root = 0

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 0
