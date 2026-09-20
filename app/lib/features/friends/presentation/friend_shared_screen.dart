import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../../l10n/app_localizations.dart';
import '../cubit/friends_cubit.dart';
import '../cubit/friends_state.dart';
import '../models/friendship.dart';

class FriendSharedScreen extends StatefulWidget {
  const FriendSharedScreen({super.key, required this.friend});

  final Friend friend;

  @override
  State<FriendSharedScreen> createState() => _FriendSharedScreenState();
}

class _FriendSharedScreenState extends State<FriendSharedScreen> {
  @override
  void initState() {
    super.initState();
    context.read<FriendsCubit>().loadSharedWithMe();
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(title: Text(widget.friend.user.displayName)),
      body: BlocBuilder<FriendsCubit, FriendsState>(
        builder: (context, state) {
          final shared = state.sharedWithMe;
          if (shared == null) {
            return const Center(child: CircularProgressIndicator());
          }
          final outfits = shared.outfits
              .where((outfit) => outfit.ownerId == widget.friend.user.id)
              .toList();
          return RefreshIndicator(
            onRefresh: () => context.read<FriendsCubit>().loadSharedWithMe(),
            child: ListView(
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
                  child: Text(l10n.sharedOutfits, style: const TextStyle(fontWeight: FontWeight.bold)),
                ),
                if (outfits.isEmpty)
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(l10n.noSharedOutfits),
                  ),
                for (final outfit in outfits)
                  ListTile(
                    leading: const Icon(Icons.checkroom),
                    title: Text(outfit.name),
                    subtitle: Text(l10n.itemsCount(outfit.items.length)),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () => context.push('/outfits/detail', extra: outfit),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}
