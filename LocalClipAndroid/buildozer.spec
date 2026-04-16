# (list) Application requirements 
# This is the "on" version you just sent. It is correct.
requirements = python3,kivy==2.3.0,ffmpeg,ffpyplayer,pillow,plyer,hostpython3,openssl

# (str) The Architecture 
# CRITICAL: Use only this for the T310 Octa-Core chip. 
# arm64-v8a is likely what was causing the "Open and Shut" crash.
android.archs = armeabi-v7a

# (str) Presplash and Icon
# Ensure these image files are small (under 500KB) so the RAM doesn't choke.
presplash.filename = %(source.dir)s/splash-screen.png
icon.filename = %(source.dir)s/Ikon.png

# (str) The Identity Fix
# This ensures the black background and no white borders.
android.adaptive_icon_background = #000000
android.adaptive_icon_foreground = %(source.dir)s/Ikon.png

# (list) Permissions
# These allow the app to actually see your equestrian archives.
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO
