import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/auth_interceptor.dart';
import '../models/outfit.dart';

class OutfitsRepository {
  OutfitsRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<List<Outfit>> listOutfits() async {
    try {
      final response = await _apiClient.dio.get('/outfits');
      return (response.data as List<dynamic>)
          .map((e) => Outfit.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<Outfit> createOutfit(String name) async {
    try {
      final response = await _apiClient.dio.post('/outfits', data: {'name': name});
      return Outfit.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<void> deleteOutfit(String id) async {
    try {
      await _apiClient.dio.delete('/outfits/$id');
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<Outfit> setOutfitItems(String outfitId, List<String> clothingItemIds) async {
    try {
      final response = await _apiClient.dio.put(
        '/outfits/$outfitId/items',
        data: {'clothing_item_ids': clothingItemIds},
      );
      return Outfit.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }
}
