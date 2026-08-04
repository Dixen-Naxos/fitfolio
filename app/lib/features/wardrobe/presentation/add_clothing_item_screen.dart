import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:image_picker/image_picker.dart';

import '../cubit/wardrobe_cubit.dart';
import '../models/clothing_item.dart';

class AddClothingItemScreen extends StatefulWidget {
  const AddClothingItemScreen({super.key});

  @override
  State<AddClothingItemScreen> createState() => _AddClothingItemScreenState();
}

class _AddClothingItemScreenState extends State<AddClothingItemScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _colorController = TextEditingController();
  ClothingCategory _category = ClothingCategory.top;
  XFile? _pickedImage;
  bool _saving = false;

  @override
  void dispose() {
    _nameController.dispose();
    _colorController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    final image = await ImagePicker().pickImage(source: source, imageQuality: 85);
    if (image != null) {
      setState(() => _pickedImage = image);
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    setState(() => _saving = true);

    final cubit = context.read<WardrobeCubit>();
    await cubit.addItem(
      name: _nameController.text.trim(),
      category: _category,
      color: _colorController.text.trim().isEmpty ? null : _colorController.text.trim(),
    );

    final newItem = cubit.state.items.isNotEmpty ? cubit.state.items.first : null;
    if (newItem != null && _pickedImage != null) {
      final bytes = await _pickedImage!.readAsBytes();
      await cubit.uploadImage(newItem.id, bytes);
    }

    if (mounted) Navigator.of(context).pop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add clothing item')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              Center(
                child: GestureDetector(
                  onTap: () => showModalBottomSheet(
                    context: context,
                    builder: (context) => SafeArea(
                      child: Wrap(
                        children: [
                          ListTile(
                            leading: const Icon(Icons.photo_camera),
                            title: const Text('Take a photo'),
                            onTap: () {
                              Navigator.of(context).pop();
                              _pickImage(ImageSource.camera);
                            },
                          ),
                          ListTile(
                            leading: const Icon(Icons.photo_library),
                            title: const Text('Choose from gallery'),
                            onTap: () {
                              Navigator.of(context).pop();
                              _pickImage(ImageSource.gallery);
                            },
                          ),
                        ],
                      ),
                    ),
                  ),
                  child: Container(
                    height: 160,
                    width: 160,
                    decoration: BoxDecoration(
                      color: Theme.of(context).colorScheme.surfaceContainerHighest,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    clipBehavior: Clip.antiAlias,
                    child: _pickedImage != null
                        ? Image.file(File(_pickedImage!.path), fit: BoxFit.cover)
                        : const Icon(Icons.add_a_photo, size: 40),
                  ),
                ),
              ),
              const SizedBox(height: 24),
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(labelText: 'Name'),
                validator: (value) => (value == null || value.trim().isEmpty) ? 'Required' : null,
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<ClothingCategory>(
                value: _category,
                decoration: const InputDecoration(labelText: 'Category'),
                items: [
                  for (final category in ClothingCategory.values)
                    DropdownMenuItem(value: category, child: Text(category.label)),
                ],
                onChanged: (value) => setState(() => _category = value ?? _category),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _colorController,
                decoration: const InputDecoration(labelText: 'Color (optional)'),
              ),
              const SizedBox(height: 24),
              FilledButton(
                onPressed: _saving ? null : _submit,
                child: _saving
                    ? const SizedBox(height: 16, width: 16, child: CircularProgressIndicator(strokeWidth: 2))
                    : const Text('Save'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
