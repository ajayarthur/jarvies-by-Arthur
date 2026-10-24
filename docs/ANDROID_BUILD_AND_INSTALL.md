# Jarvis 4.0 - Android Build & APK Installation Guide

This document provides instructions for compiling, building, and installing the standalone **Jarvis Android APK** (`.apk`) or Google Play App Bundle (`.aab`).

---

## Method 1: Cloud Build via GitHub Actions (Recommended - Zero Local Android SDK Needed)

This repository includes an automated workflow (`.github/workflows/build-apk.yml`) that builds a signed debug APK automatically on every push.

1. **Trigger the Workflow:**
   - Commit and push changes to GitHub:
     ```powershell
     cd "e:\Project files\Jarvis\jarvies-4.0-main\jarvies-4.0-main"
     call "push_to_github.bat"
     ```
   - OR go to your repository on GitHub: **Actions > Build Android APK > Run workflow**.
2. **Download the APK:**
   - Once the action finishes (typically 3–5 minutes), open the run summary.
   - Under **Artifacts**, download `Jarvies-4.0-Android-APK.zip`.
   - Extract the zip to get `app-debug.apk`.
3. **Install on Your Phone:**
   - Send `app-debug.apk` to your phone via USB, WhatsApp, Google Drive, or Bluetooth.
   - Tap the APK on your phone and select **Install**.
   - *(If prompted, tap "Allow from this source" in Android Settings).*

---

## Method 2: Local Gradle Build (Requires Android SDK & JDK 17)

If you have Android Studio or the Android Command Line Tools installed on your computer:

```powershell
# 1. Navigate to the android_app folder
cd "e:\Project files\Jarvis\jarvies-4.0-main\jarvies-4.0-main\android_app"

# 2. Generate the native Android Gradle project
npx.cmd expo prebuild --platform android

# 3. Navigate into the generated android folder
cd android

# 4. Build Debug APK using Gradle
.\gradlew.bat assembleDebug
```

The compiled APK will be located at:
```
android_app\android\app\build\outputs\apk\debug\app-debug.apk
```

To install directly to a connected phone over USB with ADB:
```powershell
adb install android\app\build\outputs\apk\debug\app-debug.apk
```

---

## Method 3: Cloud Build via Expo Application Services (EAS)

EAS Build produces production-ready APKs and AABs directly in the cloud:

```powershell
# 1. Install EAS CLI globally
npm.cmd install -g eas-cli

# 2. Log in to your free Expo account
eas login

# 3. Configure build profiles
eas build:configure

# 4. Build standalone APK for testing
eas build -p android --profile preview
```

EAS will build the APK in the cloud and output a direct download URL and QR code to install it on your device.

---

## Producing a Production Signed Release APK / AAB

To publish to Google Play Store or distribute an official signed release:

1. **Generate a Keystore:**
   ```powershell
   keytool -genkeypair -v -storetype PKCS12 -keystore jarvis-release-key.keystore -alias jarvis-key-alias -keyalg RSA -keysize 2048 -validity 10000
   ```
2. **Configure `android/app/build.gradle`:**
   Add your keystore credentials in `signingConfigs.release`.
3. **Build Release Bundle:**
   ```powershell
   cd android
   .\gradlew.bat bundleRelease
   ```
   The `.aab` will be generated at `android/app/build/outputs/bundle/release/app-release.aab`.
