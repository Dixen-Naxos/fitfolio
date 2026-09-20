import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import '../../features/auth/cubit/auth_cubit.dart';
import '../../features/auth/cubit/auth_state.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/presentation/register_screen.dart';
import '../../features/friends/models/friendship.dart';
import '../../features/friends/presentation/friend_shared_screen.dart';
import '../../features/outfits/models/outfit.dart';
import '../../features/outfits/presentation/create_outfit_screen.dart';
import '../../features/outfits/presentation/outfit_detail_screen.dart';
import '../../features/wardrobe/models/clothing_item.dart';
import '../../features/wardrobe/presentation/add_clothing_item_screen.dart';
import '../../features/wardrobe/presentation/clothing_item_detail_screen.dart';
import 'go_router_refresh_stream.dart';
import 'home_shell.dart';

GoRouter buildRouter(AuthCubit authCubit) {
  return GoRouter(
    initialLocation: '/',
    refreshListenable: GoRouterRefreshStream(authCubit.stream),
    redirect: (context, state) {
      final status = authCubit.state.status;
      final loggingIn = state.matchedLocation == '/login' || state.matchedLocation == '/register';

      if (status == AuthStatus.unknown || status == AuthStatus.authenticating) {
        return null;
      }
      if (status != AuthStatus.authenticated && !loggingIn) {
        return '/login';
      }
      if (status == AuthStatus.authenticated && loggingIn) {
        return '/';
      }
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (context, state) => const LoginScreen()),
      GoRoute(path: '/register', builder: (context, state) => const RegisterScreen()),
      GoRoute(path: '/', builder: (context, state) => const HomeShell()),
      GoRoute(path: '/wardrobe/add', builder: (context, state) => const AddClothingItemScreen()),
      GoRoute(path: '/outfits/create', builder: (context, state) => const CreateOutfitScreen()),
      GoRoute(
        path: '/outfits/detail',
        builder: (context, state) => OutfitDetailScreen(outfit: state.extra as Outfit),
      ),
      GoRoute(
        path: '/clothes/detail',
        builder: (context, state) => ClothingItemDetailScreen(item: state.extra as ClothingItem),
      ),
      GoRoute(
        path: '/friends/shared',
        builder: (context, state) => FriendSharedScreen(friend: state.extra as Friend),
      ),
    ],
  );
}
