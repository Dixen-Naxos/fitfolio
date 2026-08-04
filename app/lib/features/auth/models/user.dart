class User {
  const User({
    required this.id,
    required this.email,
    required this.displayName,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
        id: json['id'] as String,
        email: json['email'] as String,
        displayName: json['display_name'] as String,
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  final String id;
  final String email;
  final String displayName;
  final DateTime createdAt;
}
