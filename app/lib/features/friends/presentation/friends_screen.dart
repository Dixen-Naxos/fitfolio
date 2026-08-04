import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

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
    final controller = TextEditingController();
    final email = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Add a friend'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.emailAddress,
          decoration: const InputDecoration(labelText: 'Friend\'s email'),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.of(context).pop(), child: const Text('Cancel')),
          FilledButton(
            onPressed: () => Navigator.of(context).pop(controller.text.trim()),
            child: const Text('Send request'),
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
    return Scaffold(
      appBar: AppBar(
        title: const Text('Friends'),
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
                  const Padding(
                    padding: EdgeInsets.fromLTRB(16, 16, 16, 4),
                    child: Text('Friend requests', style: TextStyle(fontWeight: FontWeight.bold)),
                  ),
                  for (final request in state.incomingRequests)
                    ListTile(
                      leading: const Icon(Icons.person_outline),
                      title: Text('Request ${request.id.substring(0, 8)}'),
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
                const Padding(
                  padding: EdgeInsets.fromLTRB(16, 16, 16, 4),
                  child: Text('Your friends', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
                if (state.friends.isEmpty)
                  const Padding(
                    padding: EdgeInsets.all(16),
                    child: Text('No friends yet. Add one using their email.'),
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
