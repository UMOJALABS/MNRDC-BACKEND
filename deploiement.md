# Déploiement du backend MNRDC sur Render

Le dépôt contient un Blueprint Render (`render.yaml`) qui décrit le service Django et son disque persistant. Le backend utilise SQLite : le fichier de base et les images téléversées sont conservés sur ce disque. Le service est configuré en région Frankfurt. Cette configuration utilise un plan payant, car les disques persistants Render ne sont pas disponibles sur le plan gratuit. Vérifiez les tarifs Render avant de créer le Blueprint.

## 1. Préparer le dépôt

1. Vérifiez que `render.yaml`, `requirements.txt` et le code sont commités et poussés sur GitHub ou GitLab.
2. Ouvrez le tableau de bord Render et choisissez **New + → Blueprint**.
3. Connectez le dépôt, choisissez la branche à déployer, puis appliquez le Blueprint. Render crée la base et le service web avec leurs variables d'environnement.

À chaque déploiement, Render installe les dépendances et collecte les fichiers statiques. La commande de pré-déploiement applique les migrations avant le démarrage de Gunicorn. `SQLITE_PATH` place la base dans `/var/data/db.sqlite3`, sur le disque persistant.

## 2. Créer le compte administrateur

Après le premier déploiement réussi, ouvrez le **Shell** du service `mnrdc-backend` dans Render et lancez :

```bash
python manage.py createsuperuser
```

L'administration sera accessible à `https://<nom-du-service>.onrender.com/admin/`. L'API publique se trouve sous `/api/`.

## 3. Images et fichiers

La base SQLite est stockée dans `/var/data/db.sqlite3`. Les fichiers envoyés via l'administration sont stockés dans `/var/data/media`, sur le même disque persistant monté par Render. Les URL `image_principale` et `images_carousel` renvoyées par l'API pointent vers ces fichiers. SQLite et ce disque conviennent à une seule instance web ; ne mettez pas plusieurs instances en parallèle. Pour une application qui doit évoluer vers plusieurs instances ou un accès concurrent important, migrer vers PostgreSQL et un stockage objet partagé.

Les fichiers statiques de l'administration (CSS, JavaScript, logo) sont collectés dans `staticfiles/` et servis par WhiteNoise. Ils ne sont pas stockés sur le disque média.

## 4. Variables d'environnement

`render.yaml` configure automatiquement `SECRET_KEY`, `DEBUG=False`, `MEDIA_ROOT`, `SQLITE_PATH` et `PYTHON_VERSION`. `ALLOWED_HOSTS` et l'origine CSRF Render sont dérivés du nom d'hôte fourni automatiquement par Render. Pour un domaine personnalisé, ajoutez son nom à la variable `ALLOWED_HOSTS` (noms séparés par des virgules) et son origine `https://...` à `CSRF_TRUSTED_ORIGINS` dans les paramètres du service.

## 5. Vérifier la mise en ligne

- Ouvrez `https://<nom-du-service>.onrender.com/api/langues/` : la route publique doit répondre en JSON.
- Ouvrez `/admin/`, connectez-vous et vérifiez qu'un téléversement d'image reste accessible après un redéploiement.
- Dans les journaux Render, vérifiez que la construction, `migrate` et le démarrage de Gunicorn se terminent sans erreur.

La base de production est distincte de `db.sqlite3` en local : créez le compte administrateur et importez ou recréez les données du catalogue sur Render. Une sauvegarde SQLite locale ne migre pas automatiquement les données ni les images. Le fichier de base et les médias sont tous deux conservés sur le disque Render ; sauvegardez-les régulièrement.
