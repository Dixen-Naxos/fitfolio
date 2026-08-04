import 'package:dio/dio.dart';

import '../../../core/network/api_client.dart';
import '../../../core/network/auth_interceptor.dart';
import '../models/friendship.dart';
import '../models/shared_with_me.dart';

class FriendsRepository {
  FriendsRepository({required ApiClient apiClient}) : _apiClient = apiClient;

  final ApiClient _apiClient;

  Future<Friendship> sendFriendRequest(String addresseeEmail) async {
    try {
      final response = await _apiClient.dio.post(
        '/friends/requests',
        data: {'addressee_email': addresseeEmail},
      );
      return Friendship.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<List<Friendship>> listFriendRequests({String? direction}) async {
    try {
      final response = await _apiClient.dio.get(
        '/friends/requests',
        queryParameters: direction != null ? {'direction': direction} : null,
      );
      return (response.data as List<dynamic>)
          .map((e) => Friendship.fromJson(e as Map<String, dynamic>))
          .toList();
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<Friendship> acceptFriendRequest(String friendshipId) async {
    try {
      final response = await _apiClient.dio.post('/friends/requests/$friendshipId/accept');
      return Friendship.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<Friendship> declineFriendRequest(String friendshipId) async {
    try {
      final response = await _apiClient.dio.post('/friends/requests/$friendshipId/decline');
      return Friendship.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<List<Friend>> listFriends() async {
    try {
      final response = await _apiClient.dio.get('/friends');
      return (response.data as List<dynamic>).map((e) => Friend.fromJson(e as Map<String, dynamic>)).toList();
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<void> shareClothingItem(String itemId, String friendEmail) async {
    try {
      await _apiClient.dio.post('/clothes/$itemId/share', data: {'shared_with_email': friendEmail});
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<void> shareOutfit(String outfitId, String friendEmail) async {
    try {
      await _apiClient.dio.post('/outfits/$outfitId/share', data: {'shared_with_email': friendEmail});
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }

  Future<SharedWithMe> sharedWithMe() async {
    try {
      final response = await _apiClient.dio.get('/shared-with-me');
      return SharedWithMe.fromJson(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      throw toApiException(e);
    }
  }
}
