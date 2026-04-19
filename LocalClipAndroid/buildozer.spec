[app]
title = LocalClip
package.name = localclip
package.domain = org.satdiva
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1.0

presplash.filename = splash-screen.png
icon.filename = Ikon.png

requirements = python3,kivy==2.3.0,pyjnius,android
android.gradle_dependencies = com.google.android.exoplayer:exoplayer:2.18.7

# THE ENGINE: This downloads the Java code for ExoPlayer
android.gradle_dependencies = "com.google.android.exoplayer:exoplayer:2.18.7"

# Permissions
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, android.permission.READ_MEDIA_VIDEO

android.api = 33
android.minapi = 21
android.ndk = 25b
android.enable_androidx = True
orientation = portrait
fullscreen = 1
