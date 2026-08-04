import 'package:flutter/foundation.dart';
import 'package:flutter/widgets.dart';

/// Hand-written localization lookup for Fitfolio.
///
/// Add a new language by creating an `AppLocalizations` subclass below and
/// registering its language code in `_AppLocalizationsDelegate`.
abstract class AppLocalizations {
  const AppLocalizations();

  static const LocalizationsDelegate<AppLocalizations> delegate = _AppLocalizationsDelegate();

  static const List<Locale> supportedLocales = [Locale('en'), Locale('fr')];

  static AppLocalizations of(BuildContext context) {
    final localizations = Localizations.of<AppLocalizations>(context, AppLocalizations);
    assert(localizations != null, 'No AppLocalizations found in context');
    return localizations!;
  }

  // App
  String get appTitle;

  // Auth - login
  String get welcomeBack;
  String get email;
  String get emailValidationError;
  String get password;
  String get passwordValidationError;
  String get logIn;
  String get noAccountRegister;

  // Auth - register
  String get createYourAccount;
  String get displayName;
  String get requiredField;
  String get createAccount;

  // Home shell
  String get wardrobeTab;
  String get outfitsTab;
  String get friendsTab;
  String get logOut;

  // Wardrobe
  String get myWardrobe;
  String get somethingWentWrong;
  String get allFilter;
  String get noClothesYet;
  String get addClothingItem;
  String get takeAPhoto;
  String get chooseFromGallery;
  String get name;
  String get category;
  String get colorOptional;
  String get save;

  // Clothing categories
  String get categoryTop;
  String get categoryBottom;
  String get categoryOuterwear;
  String get categoryShoes;
  String get categoryAccessory;
  String get categoryDress;
  String get categoryOther;

  // Outfits
  String get myOutfits;
  String get noOutfitsYet;
  String itemsCount(int count);
  String get createOutfit;
  String get outfitName;
  String get selectClothingItems;
  String get addSomeClothesFirst;
  String get saveOutfit;

  // Friends
  String get friends;
  String get addAFriend;
  String get friendsEmail;
  String get cancel;
  String get sendRequest;
  String get friendRequests;
  String requestLabel(String id);
  String get yourFriends;
  String get noFriendsYet;
}

class AppLocalizationsEn extends AppLocalizations {
  const AppLocalizationsEn();

  @override
  String get appTitle => 'Fitfolio';

  @override
  String get welcomeBack => 'Welcome back';
  @override
  String get email => 'Email';
  @override
  String get emailValidationError => 'Enter a valid email';
  @override
  String get password => 'Password';
  @override
  String get passwordValidationError => 'Minimum 8 characters';
  @override
  String get logIn => 'Log in';
  @override
  String get noAccountRegister => "Don't have an account? Register";

  @override
  String get createYourAccount => 'Create your account';
  @override
  String get displayName => 'Display name';
  @override
  String get requiredField => 'Required';
  @override
  String get createAccount => 'Create account';

  @override
  String get wardrobeTab => 'Wardrobe';
  @override
  String get outfitsTab => 'Outfits';
  @override
  String get friendsTab => 'Friends';
  @override
  String get logOut => 'Log out';

  @override
  String get myWardrobe => 'My Wardrobe';
  @override
  String get somethingWentWrong => 'Something went wrong';
  @override
  String get allFilter => 'All';
  @override
  String get noClothesYet => 'No clothes yet. Tap + to add one.';
  @override
  String get addClothingItem => 'Add clothing item';
  @override
  String get takeAPhoto => 'Take a photo';
  @override
  String get chooseFromGallery => 'Choose from gallery';
  @override
  String get name => 'Name';
  @override
  String get category => 'Category';
  @override
  String get colorOptional => 'Color (optional)';
  @override
  String get save => 'Save';

  @override
  String get categoryTop => 'Top';
  @override
  String get categoryBottom => 'Bottom';
  @override
  String get categoryOuterwear => 'Outerwear';
  @override
  String get categoryShoes => 'Shoes';
  @override
  String get categoryAccessory => 'Accessory';
  @override
  String get categoryDress => 'Dress';
  @override
  String get categoryOther => 'Other';

  @override
  String get myOutfits => 'My Outfits';
  @override
  String get noOutfitsYet => 'No outfits yet. Tap + to create one.';
  @override
  String itemsCount(int count) => '$count item${count == 1 ? '' : 's'}';
  @override
  String get createOutfit => 'Create outfit';
  @override
  String get outfitName => 'Outfit name';
  @override
  String get selectClothingItems => 'Select clothing items';
  @override
  String get addSomeClothesFirst => 'Add some clothes first.';
  @override
  String get saveOutfit => 'Save outfit';

  @override
  String get friends => 'Friends';
  @override
  String get addAFriend => 'Add a friend';
  @override
  String get friendsEmail => "Friend's email";
  @override
  String get cancel => 'Cancel';
  @override
  String get sendRequest => 'Send request';
  @override
  String get friendRequests => 'Friend requests';
  @override
  String requestLabel(String id) => 'Request $id';
  @override
  String get yourFriends => 'Your friends';
  @override
  String get noFriendsYet => 'No friends yet. Add one using their email.';
}

class AppLocalizationsFr extends AppLocalizations {
  const AppLocalizationsFr();

  @override
  String get appTitle => 'Fitfolio';

  @override
  String get welcomeBack => 'Content de vous revoir';
  @override
  String get email => 'E-mail';
  @override
  String get emailValidationError => 'Entrez une adresse e-mail valide';
  @override
  String get password => 'Mot de passe';
  @override
  String get passwordValidationError => 'Minimum 8 caractères';
  @override
  String get logIn => 'Se connecter';
  @override
  String get noAccountRegister => 'Pas de compte ? Inscrivez-vous';

  @override
  String get createYourAccount => 'Créez votre compte';
  @override
  String get displayName => "Nom d'affichage";
  @override
  String get requiredField => 'Champ requis';
  @override
  String get createAccount => 'Créer un compte';

  @override
  String get wardrobeTab => 'Garde-robe';
  @override
  String get outfitsTab => 'Tenues';
  @override
  String get friendsTab => 'Amis';
  @override
  String get logOut => 'Déconnexion';

  @override
  String get myWardrobe => 'Ma garde-robe';
  @override
  String get somethingWentWrong => "Une erreur s'est produite";
  @override
  String get allFilter => 'Tous';
  @override
  String get noClothesYet => "Aucun vêtement pour l'instant. Appuyez sur + pour en ajouter.";
  @override
  String get addClothingItem => 'Ajouter un vêtement';
  @override
  String get takeAPhoto => 'Prendre une photo';
  @override
  String get chooseFromGallery => 'Choisir depuis la galerie';
  @override
  String get name => 'Nom';
  @override
  String get category => 'Catégorie';
  @override
  String get colorOptional => 'Couleur (facultatif)';
  @override
  String get save => 'Enregistrer';

  @override
  String get categoryTop => 'Haut';
  @override
  String get categoryBottom => 'Bas';
  @override
  String get categoryOuterwear => "Vêtement d'extérieur";
  @override
  String get categoryShoes => 'Chaussures';
  @override
  String get categoryAccessory => 'Accessoire';
  @override
  String get categoryDress => 'Robe';
  @override
  String get categoryOther => 'Autre';

  @override
  String get myOutfits => 'Mes tenues';
  @override
  String get noOutfitsYet => "Aucune tenue pour l'instant. Appuyez sur + pour en créer une.";
  @override
  String itemsCount(int count) => '$count article${count > 1 ? 's' : ''}';
  @override
  String get createOutfit => 'Créer une tenue';
  @override
  String get outfitName => 'Nom de la tenue';
  @override
  String get selectClothingItems => 'Sélectionnez des vêtements';
  @override
  String get addSomeClothesFirst => "Ajoutez d'abord des vêtements.";
  @override
  String get saveOutfit => 'Enregistrer la tenue';

  @override
  String get friends => 'Amis';
  @override
  String get addAFriend => 'Ajouter un ami';
  @override
  String get friendsEmail => "E-mail de l'ami(e)";
  @override
  String get cancel => 'Annuler';
  @override
  String get sendRequest => 'Envoyer la demande';
  @override
  String get friendRequests => "Demandes d'ami";
  @override
  String requestLabel(String id) => 'Demande $id';
  @override
  String get yourFriends => 'Vos amis';
  @override
  String get noFriendsYet => "Aucun ami pour l'instant. Ajoutez-en un avec son e-mail.";
}

class _AppLocalizationsDelegate extends LocalizationsDelegate<AppLocalizations> {
  const _AppLocalizationsDelegate();

  static const _supportedLanguageCodes = ['en', 'fr'];

  @override
  bool isSupported(Locale locale) => _supportedLanguageCodes.contains(locale.languageCode);

  @override
  Future<AppLocalizations> load(Locale locale) {
    switch (locale.languageCode) {
      case 'fr':
        return SynchronousFuture<AppLocalizations>(const AppLocalizationsFr());
      default:
        return SynchronousFuture<AppLocalizations>(const AppLocalizationsEn());
    }
  }

  @override
  bool shouldReload(_AppLocalizationsDelegate old) => false;
}
