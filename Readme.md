# MNRDC — Musée National de la République Démocratique du Congo

Application mobile qui fait parler le patrimoine congolais.

Le visiteur scanne le QR Code d'un objet exposé. Un avatar apparaît et raconte l'histoire de l'objet : son origine, sa signification culturelle, son usage traditionnel et ses caractéristiques historiques.

## Comment ça marche

1. L'administrateur enregistre l'objet (description par langue, médias) et génère son QR Code.
2. Le visiteur scanne le QR Code avec l'application. Aucun compte n'est nécessaire.
3. L'application récupère les données de l'objet auprès de l'API.
4. L'avatar s'affiche. En arrière-plan, la description est lue à voix haute par une synthèse vocale.
5. L'avatar ne fait que donner l'illusion de raconter l'histoire : ce n'est pas une IA et il n'y a pas de conversation.

## Technologies

| Partie | Technologie | Rôle |
|---|---|---|
| **Backend** | Django (API REST) | Données, API, gestion du contenu, génération des QR Codes |
| **Application mobile** | Flutter | Scan, avatar, lecture vocale |
| **Base de données** | PostgreSQL en local (sqlite) | Stockage des objets et descriptions |

### Bibliothèques envisagées

Ces choix sont des suggestions, à confirmer au démarrage du développement.

| Besoin | Suggestion |
|---|---|
| API REST | Django REST Framework |
| Interface d'administration | Interface d'administration intégrée de Django |
| Génération des QR Codes | `qrcode` (Python) |
| Scan de QR Code | `mobile_scanner` (Flutter) |
| Lecture vocale | `flutter_tts` (Flutter) |

## Fonctionnalités

**Visiteur (application Flutter)**
- Scanner le QR Code d'un objet
- Choisir la langue
- Voir l'avatar et écouter la description
- Voir les images et médias de l'objet

**Administrateur (Django)**
- Se connecter (seul compte de la plateforme)
- Ajouter, modifier, supprimer des objets
- Saisir une description par langue
- Ajouter des médias
- Générer le QR Code d'un objet

## Règles principales

- Un seul avatar par défaut pour tous les objets.
- Pas de conversation, pas de compte visiteur.
- Un objet a une description par langue. Si la langue demandée n'existe pas, l'application utilise le français.
- Un objet a au plus un QR Code, et un QR Code identifie un seul objet.

## Modèle de données

Le diagramme de classes UML et les parcours sont dans [`mcd.md`](mcd.md).

## API (proposition)

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/objets/qr/{valeur}/?langue=fr` | Retourne l'objet, sa description dans la langue demandée et ses médias |
| `GET` | `/api/langues/` | Liste des langues disponibles |
| `GET` | `/api/avatar/` | Retourne l'avatar par défaut |

La gestion des objets, des descriptions et des QR Codes se fait par l'administrateur, protégé par connexion.

## Structure du dépôt (proposition)

```
mnrdc-backend/
├── backend/        # Projet Django (API + administration)
├── mcd.md          # Modèle de données UML
└── README.md
```
```
mnrdc-mobile/
architecture clean code 
```
## Installation

### Backend (Django)

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows : venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

L'API est alors disponible sur `http://127.0.0.1:8000/` et l'administration sur `http://127.0.0.1:8000/admin/`.

### Application (Flutter)

```bash
cd mobile
flutter pub get
flutter run
```

Pensez à indiquer l'adresse de l'API dans la configuration de l'application.

## Feuille de route

- [ ] Modèles Django et API
- [ ] Interface d'administration
- [ ] Génération des QR Codes
- [ ] Application Flutter : scan et affichage de l'objet
- [ ] Avatar et lecture vocale
- [ ] Gestion des langues
- [ ] Tests avec de vrais objets du musée

## Licence

À définir.