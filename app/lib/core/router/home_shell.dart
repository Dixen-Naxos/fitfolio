import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

import '../../features/auth/cubit/auth_cubit.dart';
import '../../features/friends/presentation/friends_screen.dart';
import '../../features/outfits/presentation/outfits_screen.dart';
import '../../features/wardrobe/presentation/wardrobe_screen.dart';

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
    return Scaffold(
      body: IndexedStack(index: _index, children: _tabs),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _index,
        onDestinationSelected: (index) => setState(() => _index = index),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.checkroom), label: 'Wardrobe'),
          NavigationDestination(icon: Icon(Icons.style), label: 'Outfits'),
          NavigationDestination(icon: Icon(Icons.people), label: 'Friends'),
        ],
      ),
      drawer: Drawer(
        child: SafeArea(
          child: ListTile(
            leading: const Icon(Icons.logout),
            title: const Text('Log out'),
            onTap: () => context.read<AuthCubit>().logout(),
          ),
        ),
      ),
    );
  }
}
