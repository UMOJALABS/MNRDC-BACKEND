# MNRDC — Backend

Backend Django du Musée National de la République Démocratique du Congo. Le visiteur scanne le QR Code d'un objet ; le frontend récupère le contenu correspondant à la langue choisie, avec les URL des images de l'objet.

## Modèle métier

Le catalogue contient deux tables : `ObjetMusee` (nom de la pièce, numéro d’inventaire numérique facultatif, et champs du QR Code) et `ContenuObjet` (titre, langue choisie parmi français, lingala, swahili et anglais, résumé TTS, description riche HTML). Une contrainte assure un contenu par objet et par langue.

La description est éditée dans l'administration avec TinyMCE, un éditeur WYSIWYG. Le contenu est enregistré en HTML et envoyé tel quel par l'API. Le frontend doit assainir ce HTML avant de l'afficher.

## API

Voir [API.md](API.md) pour le détail des routes, paramètres, réponses et erreurs.

Voir [deploiement.md](deploiement.md) pour le déploiement sur un VPS Linux avec Nginx, Gunicorn et SQLite.

- `GET /api/objets/qr/{valeur}/?langue=fr` : retourne la fiche ; si la langue n'existe pas, le français est utilisé.
- `GET /api/objets/qr/{valeur}/langues/` : retourne les langues disponibles pour cet objet.
- `GET /api/langues/` : renvoie les codes de langue présents dans les contenus.

Un QR Code absent/inactif ou un contenu absent dans la langue demandée et en français renvoie `404`.

## Administration et QR Codes

Dans l'administration (`/admin/`), chaque objet possède un QR Code. Depuis la liste des objets, le bouton **Télécharger tous les QR codes** crée une archive ZIP contenant un fichier PNG par objet. Les noms des fichiers incluent le nom et l'identifiant de l'objet. Les QR Codes inactifs sont également inclus dans cette archive.

Le logo affiché au centre des QR Codes est `musee/static/musee/images/mnrdc-logo.png`. Son chemin est défini par `MNRDC_QR_LOGO` dans `config/settings.py`. Le logo est posé sur un fond blanc opaque afin de rester visible si le PNG comporte de la transparence. Si l'image configurée est introuvable ou illisible, un badge MNRDC de remplacement est généré.

## Installation (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Le fichier `.env` contient les réglages locaux et n'est pas versionné. Modifiez-le si nécessaire; `.env.example` sert de modèle pour le VPS.

Administration : http://127.0.0.1:8000/admin/ . SQLite est utilisé en développement local.
