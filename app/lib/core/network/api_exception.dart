/// Thrown for any non-2xx API response, carrying the HTTP status code and a
/// human-readable message extracted from the API's `{"detail": "..."}` body.
class ApiException implements Exception {
  ApiException(this.statusCode, this.message);

  final int? statusCode;
  final String message;

  @override
  String toString() => 'ApiException($statusCode): $message';
}
