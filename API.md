# API publique MNRDC

Les routes de consultation sont publiques : aucun compte visiteur ni jeton d'authentification n'est requis. Les réponses sont au format JSON. Les URL d'images renvoyées dans une fiche sont absolues et peuvent être chargées directement par le frontend.

## 1. Obtenir la fiche d'un objet par QR Code

`GET /api/objets/qr/{valeur}/?langue={code}`

Retrouve l'objet associé au QR Code et retourne sa traduction dans la langue demandée, ainsi que ses images.

### Paramètres

- `valeur` (chemin, obligatoire) : valeur inscrite dans le QR Code.
- `langue` (query, facultatif) : code de langue. Par défaut : `fr`.

### Exemple

`GET /api/objets/qr/AbC123/?langue=ln`

### Réponse — 200

```json
{
  "nom_objet": "Masque cérémoniel",
  "numero_inventaire": 125,
  "image_principale": "https://api.exemple.org/media/musee/objets/principales/masque.jpg",
  "images_carousel": [
    { "url": "https://api.exemple.org/media/musee/objets/carousel/masque-face.jpg" },
    { "url": "https://api.exemple.org/media/musee/objets/carousel/masque-detail.jpg" }
  ],
  "titre": "Masque cérémoniel",
  "langue": "ln",
  "resume": "Brève présentation destinée à la synthèse vocale.",
  "description": "<h2>Histoire</h2><p>Description détaillée de l’objet.</p>",
  "langue_demandee": "ln",
  "fallback_langue": false,
  "description_format": "html"
}
```

`image_principale` est l'URL de la photo principale, ou `null` si aucune n'est définie. `images_carousel` est un tableau d'objets contenant chacun une propriété `url`; il vaut `[]` si l'objet n'a pas d'images de carrousel. Le frontend peut afficher l'image principale comme couverture, puis les éléments de `images_carousel` dans un carrousel. Les URL sont construites à partir de l'hôte de la requête et du chemin des fichiers servis par Django.

`numero_inventaire` vaut `null` si l'objet n'en a pas. La description est du HTML produit par l'éditeur WYSIWYG. Le frontend doit l'assainir avant de l'afficher.

Si l'objet n'a pas de contenu dans la langue demandée, l'API cherche le français (`fr`). Lorsque ce repli est utilisé, `langue` vaut `fr` et `fallback_langue` vaut `true`.

### Erreurs

- `404` : QR Code inconnu ou désactivé.
- `404` : aucune traduction dans la langue demandée ni en français.
- `405` : méthode HTTP différente de GET.

## 2. Lister les langues disponibles pour un objet

`GET /api/objets/qr/{valeur}/langues/`

Retourne uniquement les langues dans lesquelles cet objet possède une traduction.

### Exemple de réponse — 200

```json
[
  { "code": "fr", "nom": "Français" },
  { "code": "ln", "nom": "Lingala" }
]
```

- `404` : QR Code inconnu ou désactivé.
- `405` : méthode HTTP différente de GET.

## 3. Lister les langues du catalogue

`GET /api/langues/`

Retourne les langues utilisées par au moins un contenu, tous objets confondus. Contrairement à la route précédente, cette liste n'est pas limitée à un objet précis. La réponse utilise le même format que la liste des langues d'un objet.

## QR Codes dans l'administration

Les QR Codes PNG sont générés par le backend et utilisent la valeur `qr_valeur` de chaque objet. Dans l'administration, la liste des objets propose **Télécharger tous les QR codes**. Cette action télécharge une archive ZIP contenant un PNG par objet, y compris les objets dont le QR Code est désactivé. Ce téléchargement est réservé aux utilisateurs connectés à l'administration ; il ne fait pas partie des routes publiques JSON décrites ci-dessus.

Le logo central est chargé depuis `musee/static/musee/images/mnrdc-logo.png`, selon le réglage `MNRDC_QR_LOGO` dans `config/settings.py`. Un fond blanc opaque derrière le logo préserve sa visibilité et le contraste des QR Codes.
