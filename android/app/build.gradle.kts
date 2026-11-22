plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "br.com.philips.pocketzapper"
    compileSdk = 35

    defaultConfig {
        applicationId = "br.com.philips.philips2"
        minSdk = 23
        targetSdk = 35
        versionCode = 2
        versionName = "2.0.0"
    }

    // Keep Java and Kotlin bytecode targets aligned for reproducible Android builds.
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }
}
