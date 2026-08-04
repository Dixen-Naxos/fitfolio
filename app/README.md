# Fitfolio (Flutter app)

Mobile app (iOS + Android) for Fitfolio: store your clothes, build outfits, and share them with
friends.

## Stack

- Flutter, Dart
- `flutter_bloc` (Cubit) for state management, feature-first folder structure
- `dio` for networking with an auth interceptor (attaches JWT, refreshes on 401)
- `go_router` for navigation + auth-gated redirects
- `flutter_secure_storage` for persisting tokens (Keychain / Keystore)
- `image_picker` for capturing/selecting clothing photos

## One-time setup

This repository includes the Dart source (`lib/`, `pubspec.yaml`, `test/`) but not the generated
native platform projects (`ios/`, `android/`), since those are produced by the Flutter tooling and
weren't available in the environment this was scaffolded in. Generate them once on a machine with
the Flutter SDK installed:

```bash
cd app
flutter create --org com.fitfolio --project-name fitfolio .
flutter pub get
```

`flutter create .` on an existing project only adds the missing platform folders; it will not
overwrite `lib/` or `pubspec.yaml`.

### Camera/gallery permissions (required for `image_picker`)

After generating the platform folders, add:
- **iOS** (`ios/Runner/Info.plist`): `NSCameraUsageDescription` and `NSPhotoLibraryUsageDescription` keys.
- **Android** (`android/app/src/main/AndroidManifest.xml`): the `CAMERA` permission (Android 13+
  also needs `READ_MEDIA_IMAGES`); `image_picker`'s install docs list the exact entries.

## Running

Point the app at your API instance (see the root [README](../README.md) to start it via Docker
Compose):

```bash
flutter run --dart-define=API_BASE_URL=http://localhost:8000/api/v1
```

Notes on `API_BASE_URL`:
- Android emulator: use `http://10.0.2.2:8000/api/v1` (this is the default) to reach your host machine.
- iOS simulator: `http://localhost:8000/api/v1` works directly.
- Physical device: use your machine's LAN IP, e.g. `http://192.168.1.20:8000/api/v1`.

## Tests

```bash
flutter test
```

## Project layout

```
lib/
  main.dart                     App entrypoint: providers, router wiring
  core/
    config/app_config.dart      API_BASE_URL (via --dart-define)
    network/                    ApiClient (dio), auth interceptor, ApiException
    storage/token_storage.dart  Secure storage for access/refresh tokens
    router/                     go_router config, auth redirect, bottom-nav shell
    theme/app_theme.dart
  features/
    auth/        models, repository, cubit, login/register screens
    wardrobe/     clothing item model, repository (incl. image upload flow), cubit, screens
    outfits/      outfit model, repository, cubit, screens (create/list)
    friends/      friend requests, sharing, "shared with me", cubit, screens
```
