import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../cubit/wardrobe_cubit.dart';
import '../cubit/wardrobe_state.dart';
import '../models/clothing_item.dart';

class WardrobeScreen extends StatefulWidget {
  const WardrobeScreen({super.key});

  @override
  State<WardrobeScreen> createState() => _WardrobeScreenState();
}

class _WardrobeScreenState extends State<WardrobeScreen> {
  ClothingCategory? _filter;

  @override
  void initState() {
    super.initState();
    context.read<WardrobeCubit>().loadItems();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Wardrobe')),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/wardrobe/add'),
        child: const Icon(Icons.add_a_photo),
      ),
      body: BlocBuilder<WardrobeCubit, WardrobeState>(
        builder: (context, state) {
          if (state.status == WardrobeStatus.loading || state.status == WardrobeStatus.initial) {
            return const Center(child: CircularProgressIndicator());
          }
          if (state.status == WardrobeStatus.error) {
            return Center(child: Text(state.errorMessage ?? 'Something went wrong'));
          }

          final items = _filter == null
              ? state.items
              : state.items.where((i) => i.category == _filter).toList();

          return RefreshIndicator(
            onRefresh: () => context.read<WardrobeCubit>().loadItems(),
            child: Column(
              children: [
                SizedBox(
                  height: 48,
                  child: ListView(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    children: [
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 4),
                        child: ChoiceChip(
                          label: const Text('All'),
                          selected: _filter == null,
                          onSelected: (_) => setState(() => _filter = null),
                        ),
                      ),
                      for (final category in ClothingCategory.values)
                        Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 4),
                          child: ChoiceChip(
                            label: Text(category.label),
                            selected: _filter == category,
                            onSelected: (_) => setState(() => _filter = category),
                          ),
                        ),
                    ],
                  ),
                ),
                Expanded(
                  child: items.isEmpty
                      ? const Center(child: Text('No clothes yet. Tap + to add one.'))
                      : GridView.builder(
                          padding: const EdgeInsets.all(12),
                          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                            crossAxisCount: 2,
                            mainAxisSpacing: 12,
                            crossAxisSpacing: 12,
                            childAspectRatio: 0.8,
                          ),
                          itemCount: items.length,
                          itemBuilder: (context, index) => _ClothingItemCard(item: items[index]),
                        ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}

class _ClothingItemCard extends StatelessWidget {
  const _ClothingItemCard({required this.item});

  final ClothingItem item;

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            child: item.imageUrl != null
                ? Image.network(item.imageUrl!, fit: BoxFit.cover)
                : Container(
                    color: Theme.of(context).colorScheme.surfaceContainerHighest,
                    child: const Icon(Icons.checkroom, size: 48),
                  ),
          ),
          Padding(
            padding: const EdgeInsets.all(8),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item.name, maxLines: 1, overflow: TextOverflow.ellipsis),
                Text(
                  item.category.label,
                  style: Theme.of(context).textTheme.bodySmall,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
