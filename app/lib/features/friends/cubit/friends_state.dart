import 'package:equatable/equatable.dart';

import '../models/friendship.dart';

enum FriendsStatus { initial, loading, loaded, error }

class FriendsState extends Equatable {
  const FriendsState({
    this.status = FriendsStatus.initial,
    this.friends = const [],
    this.incomingRequests = const [],
    this.errorMessage,
  });

  final FriendsStatus status;
  final List<Friend> friends;
  final List<Friendship> incomingRequests;
  final String? errorMessage;

  FriendsState copyWith({
    FriendsStatus? status,
    List<Friend>? friends,
    List<Friendship>? incomingRequests,
    String? errorMessage,
  }) =>
      FriendsState(
        status: status ?? this.status,
        friends: friends ?? this.friends,
        incomingRequests: incomingRequests ?? this.incomingRequests,
        errorMessage: errorMessage,
      );

  @override
  List<Object?> get props => [status, friends, incomingRequests, errorMessage];
}
