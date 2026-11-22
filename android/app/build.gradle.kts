plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "br.com.philips.pocketzapper"
    compileSdk = 35

    defaultConfig {
        val buildVersion = providers.gradleProperty("versionCode").orNull ?: "1"
        applicationId = "br.com.philips.pocketzapper"
        minSdk = 23
        targetSdk = 35
        versionCode = buildVersion.toInt()
        versionName = "1.0.$buildVersion"
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
