import 'dart:io';

import 'package:flutter/foundation.dart' show kIsWeb;

/// App-wide configuration, populated via `--dart-define` at build/run time.
///
/// Example:
///   flutter run --dart-define=API_BASE_URL=http://localhost:8000/api/v1
class AppConfig {
  const AppConfig._();

  /// Explicit override, always wins when provided (e.g. pointing a physical
  /// device at your machine's LAN IP: `--dart-define=API_BASE_URL=http://192.168.1.23:8000/api/v1`).
  static const String _apiBaseUrlOverride = String.fromEnvironment('API_BASE_URL');

  /// Falls back to a sensible per-platform default for local development:
  /// - Web / iOS simulator / desktop can reach the host machine via `localhost`.
  /// - Android emulator needs the special `10.0.2.2` alias to reach the host machine.
  static String get apiBaseUrl {
    if (_apiBaseUrlOverride.isNotEmpty) return _apiBaseUrlOverride;
    if (kIsWeb) return 'http://localhost:8000/api/v1';
    if (Platform.isAndroid) return 'http://10.0.2.2:8000/api/v1';
    return 'http://localhost:8000/api/v1';
  }
}
