import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../features/auth/cubit/auth_cubit.dart';
import '../../features/friends/presentation/friends_screen.dart';
import '../../features/outfits/presentation/outfits_screen.dart';
import '../../features/wardrobe/presentation/wardrobe_screen.dart';
import '../../l10n/app_localizations.dart';

class HomeShell extends StatefulWidget {
  const HomeShell({super.key});

  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int _index = 0;

  static const _tabs = [WardrobeScreen(), OutfitsScreen(), FriendsScreen()];

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    return Scaffold(
      body: IndexedStack(index: _index, children: _tabs),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (index) => setState(() => _index = index),
        destinations: [
          NavigationDestination(icon: const Icon(Icons.checkroom), label: l10n.wardrobeTab),
          NavigationDestination(icon: const Icon(Icons.style), label: l10n.outfitsTab),
          NavigationDestination(icon: const Icon(Icons.people), label: l10n.friendsTab),
        ],
      ),
      drawer: Drawer(
        child: SafeArea(
          child: ListTile(
            leading: const Icon(Icons.logout),
            title: Text(l10n.logOut),
            onTap: () => context.read<AuthCubit>().logout(),
          ),
        ),
      ),
    );
  }
}
