import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../cubit/outfits_cubit.dart';
import '../cubit/outfits_state.dart';
import '../models/outfit.dart';

class OutfitsScreen extends StatefulWidget {
  const OutfitsScreen({super.key});

  @override
  State<OutfitsScreen> createState() => _OutfitsScreenState();
}

class _OutfitsScreenState extends State<OutfitsScreen> {
  @override
  void initState() {
    super.initState();
    context.read<OutfitsCubit>().loadOutfits();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Outfits')),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/outfits/create'),
        child: const Icon(Icons.add),
      ),
      body: BlocBuilder<OutfitsCubit, OutfitsState>(
        builder: (context, state) {
          if (state.status == OutfitsStatus.loading || state.status == OutfitsStatus.initial) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state.status == OutfitsStatus.error) {
            return Center(child: Text(state.errorMessage ?? 'Something went wrong'));
          }
          if (state.outfits.isEmpty) {
            return const Center(child: Text('No outfits yet. Tap + to create one.'));
          }
          return RefreshIndicator(
            onRefresh: () => context.read<OutfitsCubit>().loadOutfits(),
            child: ListView.builder(
              itemCount: state.outfits.length,
              itemBuilder: (context, index) => _OutfitTile(outfit: state.outfits[index]),
            ),
          );
        },
      ),
    );
  }
}

class _OutfitTile extends StatelessWidget {
  const _OutfitTile({required this.outfit});

  final Outfit outfit;

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: const Icon(Icons.checkroom),
      title: Text(outfit.name),
      subtitle: Text('${outfit.items.length} item(s)'),
      trailing: IconButton(
        icon: const Icon(Icons.delete_outline),
        onPressed: () => context.read<OutfitsCubit>().deleteOutfit(outfit.id),
      ),
    );
  }
}
