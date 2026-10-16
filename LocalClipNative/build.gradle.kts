plugins {
    id("com.android.application") version "8.9.1"
    id("org.jetbrains.kotlin.android") version "2.0.21"
}

android {
    namespace = "org.satdiva.localclip"
    compileSdk = 36
    defaultConfig {
        applicationId = "org.satdiva.localclip"
        minSdk = 29
        targetSdk = 36
        versionCode = 2
        versionName = "0.1.2"
    }
    sourceSets {
        getByName("main") {
            manifest.srcFile("AndroidManifest.xml")
            java.setSrcDirs(listOf("code"))
            res.setSrcDirs(listOf("res"))
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}
