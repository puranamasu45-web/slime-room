# slime_room

`slime_room` is a small Flutter / Android game project.

The first release target is a simple one-screen mini game:

- A soft blue slime sits in the center of the screen.
- The slime bounces when tapped.
- The tap counter increases toward `10000`.
- The game shows a goal message at `10000 / 10000`.
- Progress is saved locally on the device.
- A reset button lets the player start over.

## App settings

| Item | Value |
| --- | --- |
| App display name | `slime_room` |
| Android package / applicationId | `com.puranamasu45.slime_room` |
| Platform target | Android first |
| Framework | Flutter |

## First release policy

This first version is intentionally minimal for Google Play testing.

- No ads
- No in-app purchases
- No network access
- No account system
- No external API
- No special permissions
- No user data collection planned

## Repository steps

1. Add Flutter project metadata. ✅
2. Add the one-screen slime tapping game in `lib/main.dart`. ✅
3. Add Android build configuration using `com.puranamasu45.slime_room`. ✅
4. Add GitHub Actions to build an Android App Bundle (`.aab`). ✅
5. Add a debug APK artifact for direct device testing. ✅

## Build from GitHub Actions

The workflow is available at:

```text
.github/workflows/build-android.yml
```

It runs automatically when `main` changes under `lib/`, `android/`, `pubspec.yaml`, or the workflow file. It can also be started manually from the GitHub Actions tab with **Build Android AAB and APK**.

The workflow creates two downloadable artifacts.

### Google Play upload artifact

```text
slime_room-release-aab
```

Inside the artifact, the expected bundle path is:

```text
build/app/outputs/bundle/release/app-release.aab
```

Use this `.aab` for Google Play Console upload after proper release signing is configured.

### Direct install test artifact

```text
slime_room-debug-apk
```

Inside the artifact, the expected APK path is:

```text
build/app/outputs/flutter-apk/app-debug.apk
```

Use this `.apk` for quick Android device testing. On the phone, allow installation from the app you use to open the file if Android asks for permission.

## Local build

If you build locally with Flutter installed:

```bash
flutter pub get
flutter build appbundle --release
flutter build apk --debug
```

The expected output paths will be:

```text
build/app/outputs/bundle/release/app-release.aab
build/app/outputs/flutter-apk/app-debug.apk
```

## Signing note

The CI workflow can build without release signing secrets by falling back to the debug signing config. That artifact is useful for build verification.

For a Google Play upload bundle, add these repository secrets and rerun the workflow:

```text
KEYSTORE_BASE64
KEYSTORE_PASSWORD
KEY_ALIAS
KEY_PASSWORD
```

`KEYSTORE_BASE64` should contain the Base64-encoded `.jks` upload keystore. Do not commit keystore files or passwords to the repository.

## Android note

The Android package / applicationId is fixed as:

```text
com.puranamasu45.slime_room
```

The app is configured without ads, billing, network permission, or special Android permissions.
