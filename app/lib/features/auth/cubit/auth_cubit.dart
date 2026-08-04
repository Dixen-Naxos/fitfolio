import 'package:flutter_bloc/flutter_bloc.dart';

import '../../../core/network/api_exception.dart';
import '../data/auth_repository.dart';
import 'auth_state.dart';

class AuthCubit extends Cubit<AuthState> {
  AuthCubit({required AuthRepository authRepository})
      : _authRepository = authRepository,
        super(const AuthState());

  final AuthRepository _authRepository;

  Future<void> checkAuthStatus() async {
    try {
      final user = await _authRepository.getMe();
      emit(state.copyWith(status: AuthStatus.authenticated, user: user));
    } catch (_) {
      emit(state.copyWith(status: AuthStatus.unauthenticated));
    }
  }

  Future<void> register({
    required String email,
    required String password,
    required String displayName,
  }) async {
    emit(state.copyWith(status: AuthStatus.authenticating, errorMessage: null));
    try {
      final result = await _authRepository.register(
        email: email,
        password: password,
        displayName: displayName,
      );
      emit(state.copyWith(status: AuthStatus.authenticated, user: result.user));
    } on ApiException catch (e) {
      emit(state.copyWith(status: AuthStatus.unauthenticated, errorMessage: e.message));
    }
  }

  Future<void> login({required String email, required String password}) async {
    emit(state.copyWith(status: AuthStatus.authenticating, errorMessage: null));
    try {
      final result = await _authRepository.login(email: email, password: password);
      emit(state.copyWith(status: AuthStatus.authenticated, user: result.user));
    } on ApiException catch (e) {
      emit(state.copyWith(status: AuthStatus.unauthenticated, errorMessage: e.message));
    }
  }

  Future<void> logout() async {
    await _authRepository.logout();
    emit(state.copyWith(status: AuthStatus.unauthenticated));
  }
}
