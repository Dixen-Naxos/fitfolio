import 'package:flutter_secure_storage/flutter_secure_storage.dart';

/// Persists auth tokens in the platform secure storage (Keychain / Keystore).
class TokenStorage {
  TokenStorage({FlutterSecureStorage? storage}) : _storage = storage ?? const FlutterSecureStorage();

  static const _accessTokenKey = 'fitfolio.access_token';
  static const _refreshTokenKey = 'fitfolio.refresh_token';

  final FlutterSecureStorage _storage;

  Future<String?> readAccessToken() => _storage.read(key: _accessTokenKey);

  Future<String?> readRefreshToken() => _storage.read(key: _refreshTokenKey);

  Future<void> saveTokens({required String accessToken, required String refreshToken}) async {
    await _storage.write(key: _accessTokenKey, value: accessToken);
    await _storage.write(key: _refreshTokenKey, value: refreshToken);
  }

  Future<void> saveAccessToken(String accessToken) =>
      _storage.write(key: _accessTokenKey, value: accessToken);

  Future<void> clear() async {
    await _storage.delete(key: _accessTokenKey);
    await _storage.delete(key: _refreshTokenKey);
  }
}
