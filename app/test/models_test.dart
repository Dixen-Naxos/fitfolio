import 'package:flutter_test/flutter_test.dart';

import 'package:fitfolio/features/wardrobe/models/clothing_item.dart';
import 'package:fitfolio/features/outfits/models/outfit.dart';

void main() {
  group('ClothingItem', () {
    test('fromJson parses category and optional fields', () {
      final item = ClothingItem.fromJson({
        'id': 'item-1',
        'owner_id': 'owner-1',
        'name': 'Blue Jeans',
        'category': 'bottom',
        'color': 'blue',
        'tags': ['casual'],
        'image_url': null,
        'created_at': '2026-01-01T00:00:00Z',
      });

      expect(item.name, 'Blue Jeans');
      expect(item.category, ClothingCategory.bottom);
      expect(item.color, 'blue');
      expect(item.tags, ['casual']);
      expect(item.imageUrl, isNull);
    });

    test('unknown category falls back to other', () {
      expect(ClothingCategoryX.fromApiValue('not-a-real-category'), ClothingCategory.other);
    });
  });

  group('Outfit', () {
    test('fromJson parses nested clothing items', () {
      final outfit = Outfit.fromJson({
        'id': 'outfit-1',
        'owner_id': 'owner-1',
        'name': 'Casual Friday',
        'created_at': '2026-01-01T00:00:00Z',
        'items': [
          {
            'id': 'item-1',
            'owner_id': 'owner-1',
            'name': 'Tee',
            'category': 'top',
            'color': null,
            'tags': [],
            'image_url': null,
            'created_at': '2026-01-01T00:00:00Z',
          },
        ],
      });

      expect(outfit.name, 'Casual Friday');
      expect(outfit.items, hasLength(1));
      expect(outfit.items.first.category, ClothingCategory.top);
    });
  });
}
