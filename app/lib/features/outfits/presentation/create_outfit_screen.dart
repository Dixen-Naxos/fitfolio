import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../l10n/app_localizations.dart';
import '../../wardrobe/cubit/wardrobe_cubit.dart';
import '../../wardrobe/cubit/wardrobe_state.dart';
import '../../wardrobe/models/clothing_item.dart';
import '../cubit/outfits_cubit.dart';

class CreateOutfitScreen extends StatefulWidget {
  const CreateOutfitScreen({super.key});

  @override
  State<CreateOutfitScreen> createState() => _CreateOutfitScreenState();
}

class _CreateOutfitScreenState extends State<CreateOutfitScreen> {
  final _nameController = TextEditingController();
  final Set<String> _selectedItemIds = {};
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    context.read<WardrobeCubit>().loadItems();
  }

  @override
  void dispose() {
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    if (_nameController.text.trim().isEmpty) return;
    setState(() => _saving = true);
    await context.read<OutfitsCubit>().createOutfit(
          _nameController.text.trim(),
          _selectedItemIds.toList(),
        );
    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(title: Text(l10n.createOutfit)),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: TextField(
              controller: _nameController,
              decoration: InputDecoration(labelText: l10n.outfitName),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Align(alignment: Alignment.centerLeft, child: Text(l10n.selectClothingItems)),
          ),
          Expanded(
            child: BlocBuilder<WardrobeCubit, WardrobeState>(
              builder: (context, state) {
                if (state.status == WardrobeStatus.loading || state.status == WardrobeStatus.initial) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (state.items.isEmpty) {
                  return Center(child: Text(l10n.addSomeClothesFirst));
                }
                final byCategory = <ClothingCategory, List<ClothingItem>>{};
                for (final item in state.items) {
                  byCategory.putIfAbsent(item.category, () => []).add(item);
                }
                return ListView(
                  children: [
                    for (final entry in byCategory.entries) ...[
                      Padding(
                        padding: const EdgeInsets.fromLTRB(16, 12, 16, 4),
                        child: Text(
                          entry.key.label(context),
                          style: Theme.of(context).textTheme.titleSmall,
                        ),
                      ),
                      for (final item in entry.value)
                        CheckboxListTile(
                          value: _selectedItemIds.contains(item.id),
                          title: Text(item.name),
                          secondary: item.imageUrl != null
                              ? CircleAvatar(backgroundImage: NetworkImage(item.imageUrl!))
                              : const CircleAvatar(child: Icon(Icons.checkroom)),
                          onChanged: (checked) => setState(() {
                            if (checked ?? false) {
                              _selectedItemIds.add(item.id);
                            } else {
                              _selectedItemIds.remove(item.id);
                            }
                          }),
                        ),
                    ],
                  ],
                );
              },
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: FilledButton(
              onPressed: _saving ? null : _submit,
              child: _saving
                  ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                  : Text(l10n.saveOutfit),
            ),
          ),
        ],
      ),
    );
  }
}
