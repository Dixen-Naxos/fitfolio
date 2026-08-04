import '../../wardrobe/models/clothing_item.dart';

class Outfit {
  const Outfit({
    required this.id,
    required this.ownerId,
    required this.name,
    required this.createdAt,
    this.items = const [],
  });

  factory Outfit.fromJson(Map<String, dynamic> json) => Outfit(
        id: json['id'] as String,
        ownerId: json['owner_id'] as String,
        name: json['name'] as String,
        createdAt: DateTime.parse(json['created_at'] as String),
        items: (json['items'] as List<dynamic>? ?? [])
            .map((e) => ClothingItem.fromJson(e as Map<String, dynamic>))
            .toList(),
      );

  final String id;
  final String ownerId;
  final String name;
  final DateTime createdAt;
  final List<ClothingItem> items;
}
