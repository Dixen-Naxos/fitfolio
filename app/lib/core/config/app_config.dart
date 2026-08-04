/// App-wide configuration, populated via `--dart-define` at build/run time.
///
/// Example:
///   flutter run --dart-define=API_BASE_URL=http://localhost:8000/api/v1
class AppConfig {
  const AppConfig._();

  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000/api/v1',
  );
}
