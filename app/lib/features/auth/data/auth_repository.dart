import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/auth_interceptor.dart';
import '../models/user.dart';

class AuthResult {
  AuthResult({required this.user, required this.accessToken, required this.refreshToken});

  final User user;
  final String accessToken;
  final String refreshToken;
}

class AuthRepository {
  AuthRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<AuthResult> register({
    required String email,
    required String password,
    required String displayName,
  }) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/register',
        data: {'email': email, 'password': password, 'display_name': displayName},
      );
      return _authResultFromResponse(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<AuthResult> login({required String email, required String password}) async {
    try {
      final response = await _apiClient.dio.post(
        '/auth/login',
        data: {'email': email, 'password': password},
      );
      return _authResultFromResponse(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<User> getMe() async {
    try {
      final response = await _apiClient.dio.get('/users/me');
      return User.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<void> logout() async {
    final refreshToken = await _apiClient.tokenStorage.readRefreshToken();
    try {
      if (refreshToken != null) {
        await _apiClient.dio.post('/auth/logout', data: {'refresh_token': refreshToken});
      }
    } on DioException {
      // Best-effort: still clear local tokens even if the server call fails.
    } finally {
      await _apiClient.tokenStorage.clear();
    }
  }

  Future<AuthResult> _authResultFromResponse(Map<String, dynamic> data) async {
    final user = User.fromJson(data['user'] as Map<String, dynamic>);
    final accessToken = data['access_token'] as String;
    final refreshToken = data['refresh_token'] as String;
    await _apiClient.tokenStorage.saveTokens(accessToken: accessToken, refreshToken: refreshToken);
    return AuthResult(user: user, accessToken: accessToken, refreshToken: refreshToken);
  }
}
