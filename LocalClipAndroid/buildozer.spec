[app]
title = LocalClip
package.name = localclip
package.domain = org.satdiva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.4

# THE FACE OF THE APP
icon.filename = %(source.dir)s/icon.png
presplash.filename = %(source.dir)s/presplash.png

# THE ENGINE
requirements = python3, kivy==2.3.0, ffpyplayer, ffmpeg, pyjnius, android

# THE ORIENTATION PIVOT
orientation = portrait
fullscreen = 1

# THE GOLDEN KEYS
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE, READ_MEDIA_VIDEO
android.api = 33
android.minapi = 21
android.ndk = 25b
android.manifest.request_legacy_external_storage = true
