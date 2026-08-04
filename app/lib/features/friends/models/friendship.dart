import '../../auth/models/user.dart';

enum FriendshipStatus { pending, accepted, declined, blocked }

FriendshipStatus _statusFromApi(String value) =>
    FriendshipStatus.values.firstWhere((s) => s.name == value, orElse: () => FriendshipStatus.pending);

class Friendship {
  const Friendship({
    required this.id,
    required this.requesterId,
    required this.addresseeId,
    required this.status,
  });

  factory Friendship.fromJson(Map<String, dynamic> json) => Friendship(
        id: json['id'] as String,
        requesterId: json['requester_id'] as String,
        addresseeId: json['addressee_id'] as String,
        status: _statusFromApi(json['status'] as String),
      );

  final String id;
  final String requesterId;
  final String addresseeId;
  final FriendshipStatus status;
}

class Friend {
  const Friend({required this.friendshipId, required this.user});

  factory Friend.fromJson(Map<String, dynamic> json) => Friend(
        friendshipId: json['friendship_id'] as String,
        user: User.fromJson(json['user'] as Map<String, dynamic>),
      );

  final String friendshipId;
  final User user;
}
