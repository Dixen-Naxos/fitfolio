import 'dart:typed_data';

import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/network/api_exception.dart';
import '../data/wardrobe_repository.dart';
import '../models/clothing_item.dart';
import 'wardrobe_state.dart';

class WardrobeCubit extends Cubit<WardrobeState> {
  WardrobeCubit({required WardrobeRepository wardrobeRepository})
      : _repository = wardrobeRepository,
        super(const WardrobeState());

  final WardrobeRepository _repository;

  Future<void> loadItems() async {
    emit(state.copyWith(status: WardrobeStatus.loading));
    try {
      final items = await _repository.listClothes();
      emit(state.copyWith(status: WardrobeStatus.loaded, items: items));
    } on ApiException catch (e) {
      emit(state.copyWith(status: WardrobeStatus.error, errorMessage: e.message));
    }
  }

  Future<void> addItem({
    required String name,
    required ClothingCategory category,
    String? color,
    List<String> tags = const [],
  }) async {
    try {
      final item = await _repository.createClothingItem(
        name: name,
        category: category,
        color: color,
        tags: tags,
      );
      emit(state.copyWith(items: [item, ...state.items]));
    } on ApiException catch (e) {
      emit(state.copyWith(errorMessage: e.message));
    }
  }

  Future<void> deleteItem(String id) async {
    try {
      await _repository.deleteClothingItem(id);
      emit(state.copyWith(items: state.items.where((i) => i.id != id).toList()));
    } on ApiException catch (e) {
      emit(state.copyWith(errorMessage: e.message));
    }
  }

  Future<void> uploadImage(String itemId, Uint8List bytes) async {
    try {
      final updated = await _repository.uploadImage(itemId, bytes);
      emit(
        state.copyWith(
          items: state.items.map((i) => i.id == itemId ? updated : i).toList(),
        ),
      );
    } on ApiException catch (e) {
      emit(state.copyWith(errorMessage: e.message));
    }
  }
}
