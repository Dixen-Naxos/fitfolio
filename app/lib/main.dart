import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:go_router/go_router.dart';

import 'core/network/api_client.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'features/auth/cubit/auth_cubit.dart';
import 'features/auth/data/auth_repository.dart';
import 'features/friends/cubit/friends_cubit.dart';
import 'features/friends/data/friends_repository.dart';
import 'features/outfits/cubit/outfits_cubit.dart';
import 'features/outfits/data/outfits_repository.dart';
import 'features/wardrobe/cubit/wardrobe_cubit.dart';
import 'features/wardrobe/data/wardrobe_repository.dart';

void main() {
  runApp(const FitfolioApp());
}

class FitfolioApp extends StatelessWidget {
  const FitfolioApp({super.key});

  @override
  Widget build(BuildContext context) {
    final apiClient = ApiClient();

    return MultiRepositoryProvider(
      providers: [
        RepositoryProvider(create: (_) => AuthRepository(apiClient: apiClient)),
        RepositoryProvider(create: (_) => WardrobeRepository(apiClient: apiClient)),
        RepositoryProvider(create: (_) => OutfitsRepository(apiClient: apiClient)),
        RepositoryProvider(create: (_) => FriendsRepository(apiClient: apiClient)),
      ],
      child: MultiBlocProvider(
        providers: [
          BlocProvider(
            create: (context) =>
                AuthCubit(authRepository: context.read<AuthRepository>())..checkAuthStatus(),
          ),
          BlocProvider(
            create: (context) => WardrobeCubit(wardrobeRepository: context.read<WardrobeRepository>()),
          ),
          BlocProvider(
            create: (context) => OutfitsCubit(outfitsRepository: context.read<OutfitsRepository>()),
          ),
          BlocProvider(
            create: (context) => FriendsCubit(friendsRepository: context.read<FriendsRepository>()),
          ),
        ],
        child: Builder(
          builder: (context) {
            final GoRouter router = buildRouter(context.read<AuthCubit>());
            return MaterialApp.router(
              title: 'Fitfolio',
              debugShowCheckedModeBanner: false,
              theme: AppTheme.light,
              routerConfig: router,
            );
          },
        ),
      ),
    );
  }
}
