import 'package:dio/dio.dart';

import '../config/app_config.dart';
import '../storage/token_storage.dart';
import 'auth_interceptor.dart';

/// Thin wrapper around a configured [Dio] instance shared by all repositories.
class ApiClient {
  ApiClient({TokenStorage? tokenStorage, String? baseUrl})
      : tokenStorage = tokenStorage ?? TokenStorage(),
        baseUrl = baseUrl ?? AppConfig.apiBaseUrl {
    dio = Dio(BaseOptions(baseUrl: this.baseUrl, connectTimeout: const Duration(seconds: 15)));
    final refreshDio = Dio(BaseOptions(connectTimeout: const Duration(seconds: 15)));
    dio.interceptors.add(
      AuthInterceptor(tokenStorage: this.tokenStorage, refreshDio: refreshDio, baseUrl: this.baseUrl),
    );
  }

  final TokenStorage tokenStorage;
  final String baseUrl;
  late final Dio dio;
}
