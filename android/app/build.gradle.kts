plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "br.com.philips.pocketzapper"
    compileSdk = 35

    defaultConfig {
        applicationId = "br.com.philips.pocketzapper"
        minSdk = 23
        targetSdk = 35
        versionCode = 1
        versionName = "1.0.0"
    }
}
