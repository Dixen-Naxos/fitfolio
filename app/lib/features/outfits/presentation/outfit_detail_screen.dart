import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../l10n/app_localizations.dart';
import '../../auth/cubit/auth_cubit.dart';
import '../../friends/cubit/friends_cubit.dart';
import '../../friends/models/friendship.dart';
import '../../wardrobe/models/clothing_item.dart';
import '../models/outfit.dart';

class OutfitDetailScreen extends StatelessWidget {
  const OutfitDetailScreen({super.key, required this.outfit});

  final Outfit outfit;

  Future<void> _share(BuildContext context) async {
    final l10n = AppLocalizations.of(context);
    final messenger = ScaffoldMessenger.of(context);
    final friendsCubit = context.read<FriendsCubit>();

    if (friendsCubit.state.friends.isEmpty) {
      await friendsCubit.loadAll();
    }
    final friends = friendsCubit.state.friends;
    if (!context.mounted) return;

    if (friends.isEmpty) {
      messenger.showSnackBar(SnackBar(content: Text(l10n.noFriendsToShareWith)));
      return;
    }

    final friend = await showModalBottomSheet<Friend>(
      context: context,
      builder: (sheetContext) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(l10n.selectAFriend, style: Theme.of(sheetContext).textTheme.titleMedium),
            ),
            for (final friend in friends)
              ListTile(
                leading: const CircleAvatar(child: Icon(Icons.person)),
                title: Text(friend.user.displayName),
                subtitle: Text(friend.user.email),
                onTap: () => Navigator.of(sheetContext).pop(friend),
              ),
          ],
        ),
      ),
    );

    if (friend == null || !context.mounted) return;

    final success = await friendsCubit.shareOutfit(outfit.id, friend.user.email);
    if (!context.mounted) return;
    messenger.showSnackBar(
      SnackBar(
        content: Text(
          success
              ? l10n.outfitSharedWith(friend.user.displayName)
              : friendsCubit.state.errorMessage ?? l10n.somethingWentWrong,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final currentUserId = context.read<AuthCubit>().state.user?.id;
    final isOwner = currentUserId != null && currentUserId == outfit.ownerId;

    return Scaffold(
      appBar: AppBar(title: Text(outfit.name)),
      floatingActionButton: isOwner
          ? FloatingActionButton.extended(
              onPressed: () => _share(context),
              icon: const Icon(Icons.share),
              label: Text(l10n.shareWithAFriend),
            )
          : null,
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
            child: Text(l10n.outfitItems, style: Theme.of(context).textTheme.titleMedium),
          ),
          Expanded(
            child: outfit.items.isEmpty
                ? Center(child: Text(l10n.emptyOutfit))
                : GridView.builder(
                    padding: const EdgeInsets.fromLTRB(12, 8, 12, 96),
                    gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      mainAxisSpacing: 12,
                      crossAxisSpacing: 12,
                      childAspectRatio: 0.8,
                    ),
                    itemCount: outfit.items.length,
                    itemBuilder: (context, index) => _OutfitItemCard(item: outfit.items[index]),
                  ),
          ),
        ],
      ),
    );
  }
}

class _OutfitItemCard extends StatelessWidget {
  const _OutfitItemCard({required this.item});

  final ClothingItem item;

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => context.push('/clothes/detail', extra: item),
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
                  const SizedBox(height: 4),
                  Text(
                    item.subcategory != null && item.subcategory!.isNotEmpty
                        ? '${item.category.label(context)} · ${AppLocalizations.of(context).subcategoryLabel(item.subcategory!)}'
                        : item.category.label(context),
                    style: Theme.of(context).textTheme.bodySmall,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
