import 'package:dio/dio.dart';

import '../storage/token_storage.dart';
import 'api_exception.dart';

/// Attaches the access token to outgoing requests and transparently retries
/// once with a refreshed access token after a 401 response.
class AuthInterceptor extends Interceptor {
  AuthInterceptor({required this.tokenStorage, required this.refreshDio, required this.baseUrl});

  final TokenStorage tokenStorage;

  /// A plain Dio instance (no interceptors) used only to call `/auth/refresh`,
  /// to avoid recursively triggering this same interceptor.
  final Dio refreshDio;
  final String baseUrl;

  bool _isRefreshing = false;

  @override
  Future<void> onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await tokenStorage.readAccessToken();
    if (token != null && options.headers['Authorization'] == null) {
      options.headers['Authorization'] = 'Bearer $token';
    }
    handler.next(options);
  }

  @override
  Future<void> onError(DioException err, ErrorInterceptorHandler handler) async {
    final response = err.response;
    final requestOptions = err.requestOptions;

    final isAuthEndpoint = requestOptions.path.contains('/auth/');
    if (response?.statusCode == 401 && !isAuthEndpoint && !_isRefreshing) {
      final refreshToken = await tokenStorage.readRefreshToken();
      if (refreshToken != null) {
        _isRefreshing = true;
        try {
          final refreshResponse = await refreshDio.post(
            '$baseUrl/auth/refresh',
            data: {'refresh_token': refreshToken},
          );
          final newAccessToken = refreshResponse.data['access_token'] as String;
          final newRefreshToken = refreshResponse.data['refresh_token'] as String;
          await tokenStorage.saveTokens(accessToken: newAccessToken, refreshToken: newRefreshToken);

          final retryOptions = requestOptions..headers['Authorization'] = 'Bearer $newAccessToken';
          final cloneReq = await refreshDio.fetch(retryOptions);
          handler.resolve(cloneReq);
          return;
        } catch (_) {
          await tokenStorage.clear();
        } finally {
          _isRefreshing = false;
        }
      }
    }
    handler.next(err);
  }
}

/// Translates a [DioException] into an [ApiException] with the API's error message.
ApiException toApiException(DioException error) {
  final data = error.response?.data;
  String message = 'Something went wrong. Please try again.';
  if (data is Map && data['detail'] != null) {
    message = data['detail'].toString();
  } else if (error.message != null) {
    message = error.message!;
  }
  return ApiException(error.response?.statusCode, message);
}
