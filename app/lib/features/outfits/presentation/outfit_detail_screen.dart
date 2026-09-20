import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

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
      body: ListView(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
            child: Text(l10n.outfitItems, style: Theme.of(context).textTheme.titleMedium),
          ),
          if (outfit.items.isEmpty)
            Padding(
              padding: const EdgeInsets.all(16),
              child: Text(l10n.emptyOutfit),
            ),
          for (final item in outfit.items)
            ListTile(
              leading: item.imageUrl != null
                  ? CircleAvatar(backgroundImage: NetworkImage(item.imageUrl!))
                  : const CircleAvatar(child: Icon(Icons.checkroom)),
              title: Text(item.name),
              subtitle: Text(item.category.label(context)),
            ),
          const SizedBox(height: 80),
        ],
      ),
    );
  }
}
