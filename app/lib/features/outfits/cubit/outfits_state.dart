import 'package:equatable/equatable.dart';

import '../models/outfit.dart';

enum OutfitsStatus { initial, loading, loaded, error }

class OutfitsState extends Equatable {
  const OutfitsState({
    this.status = OutfitsStatus.initial,
    this.outfits = const [],
    this.errorMessage,
  });

  final OutfitsStatus status;
  final List<Outfit> outfits;
  final String? errorMessage;

  OutfitsState copyWith({OutfitsStatus? status, List<Outfit>? outfits, String? errorMessage}) =>
      OutfitsState(
        status: status ?? this.status,
        outfits: outfits ?? this.outfits,
        errorMessage: errorMessage,
      );

  @override
  List<Object?> get props => [status, outfits, errorMessage];
}
