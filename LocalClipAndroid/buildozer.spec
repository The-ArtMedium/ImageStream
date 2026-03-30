[app]

title = LocalClip
package.name = localclip
package.domain = org.localclip

source.dir = .
source.include_exts = py,kv,mp4,mkv,mov,avi,webm,m4v

version = 0.1
orientation = portrait
fullscreen = 0

requirements = python3, kivy==2.2.1, ffpyplayer, cython==0.29.37

android.api = 33
android.minapi = 21
android.ndk = 27.0.12077973
android.archs = arm64-v8a, armeabi-v7a

android.permissions = READ_MEDIA_VIDEO, READ_MEDIA_IMAGES, READ_MEDIA_AUDIO

android.bootstrap = sdl2

android.allow_backup = True
android.allow_cleartext_traffic = True

log_level = 2