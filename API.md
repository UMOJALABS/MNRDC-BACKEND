# API du backend MNRDC

Les routes de consultation sont publiques : aucun compte visiteur ni jeton d'authentification n'est requis. Les réponses sont au format JSON.

## 1. Obtenir la fiche d'un objet par QR Code

`GET /api/objets/qr/{valeur}/?langue={code}`

Retrouve l'objet associé au QR Code et retourne sa traduction dans la langue demandée.

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
  "titre": "Masque cérémoniel",
  "langue": "ln",
  "resume": "Brève présentation destinée à la synthèse vocale.",
  "description": "<h2>Histoire</h2><p>Description détaillée de l’objet.</p>",
  "langue_demandee": "ln",
  "fallback_langue": false,
  "description_format": "html"
}
```

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

Retourne les langues utilisées par au moins un contenu, tous objets confondus. Contrairement à la route précédente, cette liste n'est pas limitée à un objet précis.

La réponse utilise le même format que la liste des langues d'un objet.

## Ce que l'API ne renvoie pas

L'API ne renvoie ni médias ni avatar. Elle fournit les textes et les informations de l'objet nécessaires au frontend. Le résumé est destiné à la synthèse vocale côté frontend.
