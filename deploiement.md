# Déploiement du backend MNRDC sur un VPS

Ce guide décrit un déploiement sur un VPS Ubuntu avec un sous-domaine DuckDNS, Nginx, Gunicorn et SQLite. Le code reste dans `/opt/mnrdc-backend`; la base et les images sont conservées dans `/var/lib/mnrdc`, hors du dépôt.

## 0. Créer et configurer le nom DuckDNS

1. Connectez-vous sur [DuckDNS](https://www.duckdns.org/), créez un sous-domaine (dans ton cas `mnrdc.duckdns.org`) et garde le token privé.
2. Faites pointer ce sous-domaine vers l'adresse IPv4 publique de votre VPS depuis le tableau de bord DuckDNS. Vérifiez que les ports 80 et 443 sont accessibles depuis Internet et autorisés par le pare-feu du fournisseur et celui du VPS.
3. Si l'adresse IP du VPS peut changer, configurez l'appel de mise à jour DuckDNS ci-dessous. DuckDNS répond `OK` lorsque la mise à jour réussit. Si l'IP est fixe, l'actualisation automatique n'est pas nécessaire.

Créez un fichier de configuration privé `/etc/duckdns.conf` :

```bash
sudo sh -c 'printf "DUCKDNS_DOMAIN=%s\\nDUCKDNS_TOKEN=%s\\n" "mnrdc" "COLLER_ICI_LE_TOKEN" > /etc/duckdns.conf'
sudo chmod 600 /etc/duckdns.conf
```

Le préfixe `mnrdc` correspond à `mnrdc.duckdns.org`; remplace-le si tu choisis un autre nom. Renseigne ton token DuckDNS. Crée ensuite `/usr/local/bin/update-duckdns.sh` :

```sh
#!/bin/sh
. /etc/duckdns.conf
curl -fsS "https://www.duckdns.org/update?domains=${DUCKDNS_DOMAIN}&token=${DUCKDNS_TOKEN}&ip=" -o /var/log/duckdns.log
```

Installez `curl`, rendez le script exécutable et planifiez sa mise à jour périodique :

```bash
sudo apt install -y curl
sudo chmod 700 /usr/local/bin/update-duckdns.sh
sudo /usr/local/bin/update-duckdns.sh
cat /var/log/duckdns.log
```

Le résultat attendu est `OK`. Pour le renouveler toutes les cinq minutes si votre IP change, ajoutez la ligne `*/5 * * * * root /usr/local/bin/update-duckdns.sh` dans `/etc/cron.d/duckdns`.

## 1. Installer les dépendances système

```bash
sudo apt update
sudo apt install -y python3-venv python3-pip nginx
```

Copiez ou clonez le dépôt dans `/opt/mnrdc-backend`, puis installez les dépendances Python :

```bash
cd /opt/mnrdc-backend
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

Créez un utilisateur système dédié et les dossiers persistants. Ajustez le propriétaire au nom de l'utilisateur qui exécutera Gunicorn :

```bash
sudo useradd --system --home /opt/mnrdc-backend --shell /usr/sbin/nologin mnrdc
sudo mkdir -p /var/lib/mnrdc/media
sudo chown -R mnrdc:www-data /opt/mnrdc-backend /var/lib/mnrdc
sudo chmod 750 /var/lib/mnrdc
```

## 2. Configurer les variables d'environnement

Créez `/etc/mnrdc-backend.env` et définissez une vraie clé secrète, le domaine, le chemin SQLite et le dossier média :

```ini
SECRET_KEY=remplacer-par-une-cle-aleatoire-longue
DEBUG=False
ALLOWED_HOSTS=mnrdc.duckdns.org
CSRF_TRUSTED_ORIGINS=https://mnrdc.duckdns.org
SQLITE_PATH=/var/lib/mnrdc/db.sqlite3
MEDIA_ROOT=/var/lib/mnrdc/media
```

Générez une clé avec `python -c 'import secrets; print(secrets.token_urlsafe(50))'`, puis protégez le fichier :

```bash
sudo chown root:mnrdc /etc/mnrdc-backend.env
sudo chmod 640 /etc/mnrdc-backend.env
```

`ALLOWED_HOSTS` contient le nom d'hôte seulement, sans `https://` ni chemin. `CSRF_TRUSTED_ORIGINS` contient l'origine complète en HTTPS. Si tu modifies le fichier sur le VPS, redémarre Gunicorn avec `sudo systemctl restart mnrdc-backend`. L'administration Django doit être servie en HTTPS.

## 3. Appliquer les migrations et créer l'administrateur

```bash
cd /opt/mnrdc-backend
sudo -u mnrdc .venv/bin/python manage.py migrate
sudo -u mnrdc .venv/bin/python manage.py collectstatic --noinput
sudo -u mnrdc .venv/bin/python manage.py createsuperuser
```

## 4. Lancer Gunicorn avec systemd

Créez `/etc/systemd/system/mnrdc-backend.service` :

```ini
[Unit]
Description=Backend Django MNRDC
After=network.target

[Service]
User=mnrdc
Group=www-data
WorkingDirectory=/opt/mnrdc-backend
EnvironmentFile=/etc/mnrdc-backend.env
ExecStart=/opt/mnrdc-backend/.venv/bin/gunicorn --workers 2 --bind 127.0.0.1:8000 config.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Activez le service :

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now mnrdc-backend
sudo systemctl status mnrdc-backend
```

## 5. Configurer Nginx

Créez `/etc/nginx/sites-available/mnrdc-backend` et utilise ton sous-domaine DuckDNS :

```nginx
server {
    listen 80;
    server_name mnrdc.duckdns.org;

    location /media/ {
        alias /var/lib/mnrdc/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Activez la configuration et rechargez Nginx :

```bash
sudo ln -s /etc/nginx/sites-available/mnrdc-backend /etc/nginx/sites-enabled/mnrdc-backend
sudo nginx -t
sudo systemctl reload nginx
```

Quand le nom DuckDNS résout vers le VPS et que le site répond en HTTP, installez Certbot avec `sudo snap install --classic certbot`, puis demandez le certificat et la redirection HTTPS :

```bash
sudo certbot --nginx -d mnrdc.duckdns.org
```

Certbot configure Nginx et le renouvellement du certificat. Ouvre les ports SSH, HTTP et HTTPS dans les pare-feu du VPS et du fournisseur. L'API sera accessible à `https://mnrdc.duckdns.org/api/` et l'administration à `https://mnrdc.duckdns.org/admin/`.

## 6. Connexion de l'application Flutter

Configure l'URL de base de l'API Flutter comme suit :

```text
https://mnrdc.duckdns.org/api/
```

Par exemple, la liste des langues s'obtient à `https://mnrdc.duckdns.org/api/langues/`, et une fiche QR à `https://mnrdc.duckdns.org/api/objets/qr/VALEUR_QR/?langue=fr`. `ALLOWED_HOSTS` autorise le nom de domaine pour toutes les requêtes HTTP vers Django, qu'elles viennent d'un navigateur ou de Flutter; il ne faut pas ajouter une entrée différente par application cliente. Flutter n'a pas besoin de `/admin/` et ne doit pas appeler uniquement la racine `/`.

## 7. Vérifier et sauvegarder

- `https://mnrdc.duckdns.org/api/langues/` doit retourner du JSON.
- `https://mnrdc.duckdns.org/admin/` doit afficher l'administration.
- Consultez les journaux avec `sudo journalctl -u mnrdc-backend -f`.
- Sauvegardez régulièrement `/var/lib/mnrdc/`, qui contient la base SQLite et les images téléversées.

Après une mise à jour du code, installez les éventuelles dépendances, appliquez `migrate`, lancez `collectstatic`, puis redémarrez `mnrdc-backend`. Gardez une seule instance Gunicorn pour utiliser SQLite et le stockage local des images.
