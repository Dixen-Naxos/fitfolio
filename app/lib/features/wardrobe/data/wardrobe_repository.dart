import 'dart:typed_data';

import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/auth_interceptor.dart';
import '../models/clothing_item.dart';

class WardrobeRepository {
  WardrobeRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<List<ClothingItem>> listClothes() async {
    try {
      final response = await _apiClient.dio.get('/clothes');
      return (response.data as List<dynamic>)
          .map((e) => ClothingItem.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<ClothingItem> createClothingItem({
    required String name,
    required ClothingCategory category,
    String? color,
    List<String> tags = const [],
  }) async {
    try {
      final response = await _apiClient.dio.post(
        '/clothes',
        data: {'name': name, 'category': category.apiValue, 'color': color, 'tags': tags},
      );
      return ClothingItem.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<ClothingItem> updateClothingItem(
    String id, {
    String? name,
    ClothingCategory? category,
    String? color,
    List<String>? tags,
  }) async {
    try {
      final response = await _apiClient.dio.patch(
        '/clothes/$id',
        data: {
          if (name != null) 'name': name,
          if (category != null) 'category': category.apiValue,
          if (color != null) 'color': color,
          if (tags != null) 'tags': tags,
        },
      );
      return ClothingItem.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<void> deleteClothingItem(String id) async {
    try {
      await _apiClient.dio.delete('/clothes/$id');
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  /// Uploads [bytes] as the item's photo: requests a presigned MinIO URL,
  /// PUTs the raw bytes directly to object storage, then confirms with the API.
  Future<ClothingItem> uploadImage(String itemId, Uint8List bytes, {String contentType = 'image/jpeg'}) async {
    try {
      final uploadUrlResponse = await _apiClient.dio.post(
        '/clothes/$itemId/image/upload-url',
        data: {'content_type': contentType},
      );
      final uploadUrl = uploadUrlResponse.data['upload_url'] as String;
      final objectKey = uploadUrlResponse.data['object_key'] as String;

      final plainDio = Dio();
      await plainDio.put(
        uploadUrl,
        data: bytes,
        options: Options(headers: {'Content-Type': contentType}),
      );

      final confirmResponse = await _apiClient.dio.post(
        '/clothes/$itemId/image/confirm',
        data: {'object_key': objectKey},
      );
      return ClothingItem.fromJson(confirmResponse.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }
}
