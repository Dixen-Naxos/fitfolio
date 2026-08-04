import 'package:equatable/equatable.dart';

import '../models/user.dart';

enum AuthStatus { unknown, authenticating, authenticated, unauthenticated }

class AuthState extends Equatable {
  const AuthState({this.status = AuthStatus.unknown, this.user, this.errorMessage});

  final AuthStatus status;
  final User? user;
  final String? errorMessage;

  AuthState copyWith({AuthStatus? status, User? user, String? errorMessage}) => AuthState(
        status: status ?? this.status,
        user: user ?? this.user,
        errorMessage: errorMessage,
      );

  @override
  List<Object?> get props => [status, user, errorMessage];
}
