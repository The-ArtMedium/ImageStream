[app]
# (str) Title of your application
title = My Application

# (str) Package name
package.name = org.test.myapp

# (str) Package domain
package.domain = org.test

# (str) Source files
source.include_exts = py,png,jpg,jpeg,kv,atlas

# (str) Presplash filename
presplash.filename = splash-screen.png

# (list) Application requirements
requirements = python3,kivy

# (str) Supported orientation
orientation = landscape

# (str) Icon of the application
icon.filename = icon.png

# (str) Version of the application
version = 0.1

# (bool) Whether the application is a debug build
debug = 0

[buildozer]
# (str) The target to build for (android or ios)
target = android

# (str) The Android API to use
android.api = 30

# (str) The minimum Android API
android.minapi = 21

# (str) Android SDK version
android.sdk = 30

# (str) The Android NDK version
android.ndk = 21b

# (str) Directory where the buildozer executes (the default is '.').
build_dir = ./build

# (list) Permissions for the application
android.permissions = INTERNET,ACCESS_NETWORK_STATE

# (bool) Whether to use the Gradle build
use_gradle = True

# (str) Path to your keystore
android.keystore = mykeystore.keystore

# (str) Release key alias
android.keyalias = myalias

# (str) Release key password
android.keystore.password = mypassword
