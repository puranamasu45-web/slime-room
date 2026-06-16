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

## Planned repository steps

1. Add Flutter project metadata. ✅
2. Add the one-screen slime tapping game in `lib/main.dart`. ✅
3. Add Android build configuration using `com.puranamasu45.slime_room`. ✅
4. Add GitHub Actions to build an Android App Bundle (`.aab`).

## Build note

Android build files have been added. The target artifact for Google Play will be an Android App Bundle:

```bash
flutter pub get
flutter build appbundle --release
```

The expected output path will be:

```text
build/app/outputs/bundle/release/app-release.aab
```

## Android note

The Android package / applicationId is fixed as:

```text
com.puranamasu45.slime_room
```

The app is configured without ads, billing, network permission, or special Android permissions.
