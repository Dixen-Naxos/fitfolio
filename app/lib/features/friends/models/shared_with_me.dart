import '../../outfits/models/outfit.dart';
import '../../wardrobe/models/clothing_item.dart';

class SharedWithMe {
  const SharedWithMe({required this.clothingItems, required this.outfits});

  factory SharedWithMe.fromJson(Map<String, dynamic> json) => SharedWithMe(
        clothingItems: (json['clothing_items'] as List<dynamic>? ?? [])
            .map((e) => ClothingItem.fromJson(e['clothing_item'] as Map<String, dynamic>))
            .toList(),
        outfits: (json['outfits'] as List<dynamic>? ?? [])
            .map((e) => Outfit.fromJson(e['outfit'] as Map<String, dynamic>))
            .toList(),
      );

  final List<ClothingItem> clothingItems;
  final List<Outfit> outfits;
}
