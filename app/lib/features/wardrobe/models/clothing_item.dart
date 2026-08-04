import 'package:flutter/widgets.dart';

import '../../../l10n/app_localizations.dart';

enum ClothingCategory { top, bottom, outerwear, shoes, accessory, dress, other }

extension ClothingCategoryX on ClothingCategory {
  String get apiValue => name;

  String label(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    switch (this) {
      case ClothingCategory.top:
        return l10n.categoryTop;
      case ClothingCategory.bottom:
        return l10n.categoryBottom;
      case ClothingCategory.outerwear:
        return l10n.categoryOuterwear;
      case ClothingCategory.shoes:
        return l10n.categoryShoes;
      case ClothingCategory.accessory:
        return l10n.categoryAccessory;
      case ClothingCategory.dress:
        return l10n.categoryDress;
      case ClothingCategory.other:
        return l10n.categoryOther;
    }
  }

  static ClothingCategory fromApiValue(String value) =>
      ClothingCategory.values.firstWhere((c) => c.apiValue == value, orElse: () => ClothingCategory.other);
}

class ClothingItem {
  const ClothingItem({
    required this.id,
    required this.ownerId,
    required this.name,
    required this.category,
    this.color,
    this.tags = const [],
    this.imageUrl,
    required this.createdAt,
  });

  factory ClothingItem.fromJson(Map<String, dynamic> json) => ClothingItem(
        id: json['id'] as String,
        ownerId: json['owner_id'] as String,
        name: json['name'] as String,
        category: ClothingCategoryX.fromApiValue(json['category'] as String),
        color: json['color'] as String?,
        tags: (json['tags'] as List<dynamic>? ?? []).map((e) => e as String).toList(),
        imageUrl: json['image_url'] as String?,
        createdAt: DateTime.parse(json['created_at'] as String),
      );

  final String id;
  final String ownerId;
  final String name;
  final ClothingCategory category;
  final String? color;
  final List<String> tags;
  final String? imageUrl;
  final DateTime createdAt;
}
