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
    signingConfigs {
        create("upload") {
            val ks = System.getenv("KEYSTORE_FILE")
            if (ks != null) {
                storeFile = file(ks)
                storePassword = System.getenv("KEYSTORE_PASSWORD")
                keyAlias = System.getenv("KEY_ALIAS")
                keyPassword = System.getenv("KEYSTORE_PASSWORD")
            }
        }
    }
    buildTypes {
        getByName("release") {
            if (System.getenv("KEYSTORE_FILE") != null) {
                signingConfig = signingConfigs.getByName("upload")
            }
        }
    }
    lint { checkReleaseBuilds = false }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions { jvmTarget = "17" }
}
