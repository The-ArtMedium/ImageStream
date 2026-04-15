# (list) Application requirements
# Added ffmpeg and explicitly linked ffpyplayer
requirements = python3,kivy==2.3.0,ffmpeg,ffpyplayer,pillow,hostpython3,openssl

# (list) Permissions 
# Ensure we have the "Witness" permissions for the media player
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO, READ_MEDIA_AUDIO

# (list) Custom source folders for the build
# This helps the engine find the video decoding logic
android.copy_libs = 1
