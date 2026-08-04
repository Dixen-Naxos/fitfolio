import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../l10n/app_localizations.dart';
import '../cubit/friends_cubit.dart';
import '../cubit/friends_state.dart';

class FriendsScreen extends StatefulWidget {
  const FriendsScreen({super.key});

  @override
  State<FriendsScreen> createState() => _FriendsScreenState();
}

class _FriendsScreenState extends State<FriendsScreen> {
  @override
  void initState() {
    super.initState();
    context.read<FriendsCubit>().loadAll();
  }

  Future<void> _showAddFriendDialog() async {
    final l10n = AppLocalizations.of(context);
    final controller = TextEditingController();
    final email = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(l10n.addAFriend),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.emailAddress,
          decoration: InputDecoration(labelText: l10n.friendsEmail),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(), child: Text(l10n.cancel)),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(controller.text.trim()),
            child: Text(l10n.sendRequest),
          ),
        ],
      ),
    );
    if (email != null && email.isNotEmpty && mounted) {
      await context.read<FriendsCubit>().sendRequest(email);
    }
  }

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Scaffold(
      appBar: AppBar(
        title: Text(l10n.friends),
        actions: [IconButton(icon: const Icon(Icons.person_add), onPressed: _showAddFriendDialog)],
      ),
      body: BlocConsumer<FriendsCubit, FriendsState>(
        listenWhen: (previous, current) => current.errorMessage != null,
        listener: (context, state) {
          ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(state.errorMessage!)));
        },
        builder: (context, state) {
          if (state.status == FriendsStatus.loading || state.status == FriendsStatus.initial) {
            return const Center(child: CircularProgressIndicator());
          }
          return RefreshIndicator(
            onRefresh: () => context.read<FriendsCubit>().loadAll(),
            child: ListView(
              children: [
                if (state.incomingRequests.isNotEmpty) ...[
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
                    child: Text(l10n.friendRequests, style: const TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  for (final request in state.incomingRequests)
                    ListTile(
                      leading: const Icon(Icons.person_outline),
                      title: Text(l10n.requestLabel(request.id.substring(0, 8))),
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.check, color: Colors.green),
                            onPressed: () => context.read<FriendsCubit>().accept(request.id),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close, color: Colors.red),
                            onPressed: () => context.read<FriendsCubit>().decline(request.id),
                          ),
                        ],
                      ),
                    ),
                ],
                Padding(
                  padding: const EdgeInsets.fromLTRB(16, 16, 16, 4),
                  child: Text(l10n.yourFriends, style: const TextStyle(fontWeight: FontWeight.bold)),
                ),
                if (state.friends.isEmpty)
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(l10n.noFriendsYet),
                  ),
                for (final friend in state.friends)
                  ListTile(
                    leading: const CircleAvatar(child: Icon(Icons.person)),
                    title: Text(friend.user.displayName),
                    subtitle: Text(friend.user.email),
                  ),
              ],
            ),
          );
        },
      ),
    );
  }
}
