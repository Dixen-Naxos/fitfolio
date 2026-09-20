import 'package:equatable/equatable.dart';

import '../models/friendship.dart';
import '../models/shared_with_me.dart';

enum FriendsStatus { initial, loading, loaded, error }

class FriendsState extends Equatable {
  const FriendsState({
    this.status = FriendsStatus.initial,
    this.friends = const [],
    this.incomingRequests = const [],
    this.sharedWithMe,
    this.errorMessage,
  });

  final FriendsStatus status;
  final List<Friend> friends;
  final List<Friendship> incomingRequests;
  final SharedWithMe? sharedWithMe;
  final String? errorMessage;

  FriendsState copyWith({
    FriendsStatus? status,
    List<Friend>? friends,
    List<Friendship>? incomingRequests,
    SharedWithMe? sharedWithMe,
    String? errorMessage,
  }) =>
      FriendsState(
        status: status ?? this.status,
        friends: friends ?? this.friends,
        incomingRequests: incomingRequests ?? this.incomingRequests,
        sharedWithMe: sharedWithMe ?? this.sharedWithMe,
        errorMessage: errorMessage,
      );

  @override
  List<Object?> get props => [status, friends, incomingRequests, sharedWithMe, errorMessage];
}
