import 'package:flutter/material.dart';

import '../../../l10n/app_localizations.dart';
import '../models/clothing_item.dart';

class ClothingItemDetailScreen extends StatelessWidget {
  const ClothingItemDetailScreen({super.key, required this.item});

  final ClothingItem item;

  @override
  Widget build(BuildContext context) {
    final l10n = AppLocalizations.of(context);
    final theme = Theme.of(context);
    return Scaffold(
      appBar: AppBar(title: Text(item.name)),
      body: ListView(
        children: [
          AspectRatio(
            aspectRatio: 1,
            child: Container(
              color: theme.colorScheme.surfaceContainerHighest,
              child: item.imageUrl != null
                  ? InteractiveViewer(
                      minScale: 1,
                      maxScale: 4,
                      child: Image.network(
                        item.imageUrl!,
                        fit: BoxFit.contain,
                        width: double.infinity,
                        loadingBuilder: (context, child, progress) => progress == null
                            ? child
                            : const Center(child: CircularProgressIndicator()),
                        errorBuilder: (context, error, stackTrace) =>
                            Center(child: Text(l10n.noImageAvailable)),
                      ),
                    )
                  : Center(
                      child: Icon(Icons.checkroom, size: 72, color: theme.colorScheme.onSurfaceVariant),
                    ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(item.name, style: theme.textTheme.headlineSmall),
                const SizedBox(height: 12),
                _DetailRow(label: l10n.category, value: _categoryText(context)),
                if (item.color != null && item.color!.isNotEmpty)
                  _DetailRow(label: l10n.color, value: item.color!),
                if (item.tags.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Text(l10n.tags, style: theme.textTheme.titleSmall),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: [for (final tag in item.tags) Chip(label: Text(tag))],
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _categoryText(BuildContext context) {
    final category = item.category.label(context);
    if (item.subcategory != null && item.subcategory!.isNotEmpty) {
      return '$category · ${item.subcategory}';
    }
    return category;
  }
}

class _DetailRow extends StatelessWidget {
  const _DetailRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 100,
            child: Text(label, style: theme.textTheme.bodyMedium?.copyWith(color: theme.hintColor)),
          ),
          Expanded(child: Text(value, style: theme.textTheme.bodyMedium)),
        ],
      ),
    );
  }
}
