import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/network/api_exception.dart';
import '../data/friends_repository.dart';
import 'friends_state.dart';

class FriendsCubit extends Cubit<FriendsState> {
  FriendsCubit({required FriendsRepository friendsRepository})
      : _repository = friendsRepository,
        super(const FriendsState());

  final FriendsRepository _repository;

  Future<void> loadAll() async {
    emit(state.copyWith(status: FriendsStatus.loading));
    try {
      final friends = await _repository.listFriends();
      final incoming = await _repository.listFriendRequests(direction: 'incoming');
      emit(state.copyWith(status: FriendsStatus.loaded, friends: friends, incomingRequests: incoming));
    } on ApiException catch (e) {
      emit(state.copyWith(status: FriendsStatus.error, errorMessage: e.message));
    }
  }

  Future<void> sendRequest(String email) async {
    try {
      await _repository.sendFriendRequest(email);
    } on ApiException catch (e) {
      emit(state.copyWith(errorMessage: e.message));
    }
  }

  Future<void> accept(String friendshipId) async {
    try {
      await _repository.acceptFriendRequest(friendshipId);
      await loadAll();
    } on ApiException catch (e) {
      emit(state.copyWith(errorMessage: e.message));
    }
  }

  Future<void> decline(String friendshipId) async {
    try {
      await _repository.declineFriendRequest(friendshipId);
      await loadAll();
    } on ApiException catch (e) {
      emit(state.copyWith(errorMessage: e.message));
    }
  }
}
