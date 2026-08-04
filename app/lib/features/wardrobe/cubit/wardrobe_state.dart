import 'package:equatable/equatable.dart';

import '../models/clothing_item.dart';

enum WardrobeStatus { initial, loading, loaded, error }

class WardrobeState extends Equatable {
  const WardrobeState({
    this.status = WardrobeStatus.initial,
    this.items = const [],
    this.errorMessage,
  });

  final WardrobeStatus status;
  final List<ClothingItem> items;
  final String? errorMessage;

  WardrobeState copyWith({
    WardrobeStatus? status,
    List<ClothingItem>? items,
    String? errorMessage,
  }) =>
      WardrobeState(
        status: status ?? this.status,
        items: items ?? this.items,
        errorMessage: errorMessage,
      );

  @override
  List<Object?> get props => [status, items, errorMessage];
}
