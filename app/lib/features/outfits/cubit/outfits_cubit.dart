import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/network/api_exception.dart';
import '../data/outfits_repository.dart';
import '../models/outfit.dart';
import 'outfits_state.dart';

class OutfitsCubit extends Cubit<OutfitsState> {
  OutfitsCubit({required OutfitsRepository outfitsRepository})
      : _repository = outfitsRepository,
        super(const OutfitsState());

  final OutfitsRepository _repository;

  Future<void> loadOutfits() async {
    emit(state.copyWith(status: OutfitsStatus.loading));
    try {
      final outfits = await _repository.listOutfits();
      emit(state.copyWith(status: OutfitsStatus.loaded, outfits: outfits));
    } on ApiException catch (e) {
      emit(state.copyWith(status: OutfitsStatus.error, errorMessage: e.message));
    }
  }

  Future<Outfit?> createOutfit(String name, List<String> clothingItemIds) async {
    try {
      final outfit = await _repository.createOutfit(name);
      final withItems = clothingItemIds.isEmpty
          ? outfit
          : await _repository.setOutfitItems(outfit.id, clothingItemIds);
      emit(state.copyWith(outfits: [withItems, ...state.outfits]));
      return withItems;
    } on ApiException catch (e) {
      emit(state.copyWith(errorMessage: e.message));
      return null;
    }
  }

  Future<void> deleteOutfit(String id) async {
    try {
      await _repository.deleteOutfit(id);
      emit(state.copyWith(outfits: state.outfits.where((o) => o.id != id).toList()));
    } on ApiException catch (e) {
      emit(state.copyWith(errorMessage: e.message));
    }
  }
}
