import 'package:flutter/material.dart';

class AppTheme {
  const AppTheme._();

  static ThemeData get light => ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF6750A4)),
        appBarTheme: const AppBarTheme(centerTitle: true),
      );
}
