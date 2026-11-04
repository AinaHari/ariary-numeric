# ARIARY NUMERIC

Application fintech malgache (portefeuille numérique de démonstration, blockchain de test, suivi logistique, transit/douane).

## Avertissement
- Le portefeuille est un **portefeuille de démonstration** : aucun argent réel.
- Les transferts internationaux réels sont désactivés sans partenaire autorisé.
- Les paiements mobile money réels ne sont pas disponibles dans cette version.
- La blockchain utilise un réseau de test (Sepolia) si configuré.

## Prérequis
- Python 3.12
- pip, venv

## Installation backend
```bash
cd /home/aina-ben/Desktop/ariary-numeric
python3 -m venv .venv
source .venv/bin/activate
pip install django djangorestframework django-cors-headers python-dotenv web3 qrcode pillow
cd backend
cp ../.env.example ../.env
python manage.py migrate
DJANGO_SUPERUSER_EMAIL=admin@example.com DJANGO_SUPERUSER_PASSWORD='ChangeMe!' python manage.py createsuperuser --noinput
```

## Lancer le backend
```bash
cd /home/aina-ben/Desktop/ariary-numeric/backend
source ../.venv/bin/activate
python manage.py runserver 127.0.0.1:8001
```

## Lancer l'application mobile (Flet)
```bash
cd /home/aina-ben/Desktop/ariary-numeric
source .venv/bin/activate
export ARIARY_API_BASE_URL=http://127.0.0.1:8001
PYTHONPATH=/home/aina-ben/Desktop/ariary-numeric python mobile/app.py
```

## Tests
```bash
cd /home/aina-ben/Desktop/ariary-numeric/backend
source ../.venv/bin/activate
python manage.py test
```

## Compilation Android (APK/AAB)
Flet compile via `flet build apk` / `flet build aab`. Nécessite Flutter SDK et Android SDK installés.

```bash
# Installer Flutter (Linux)
# voir https://docs.flutter.dev/get-started/install/linux
# puis
cd /home/aina-ben/Desktop/ariary-numeric
source .venv/bin/activate
flet build apk mobile/
flet build aab mobile/
```

Si Flutter/Android SDK absent, installer d'abord:
```bash
sudo snap install flutter --classic
flutter doctor
```

## Mise en ligne (production)

### Variables d'environnement requises
```bash
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=<cle-longue-aleatoire-50+-caracteres>
DJANGO_ALLOWED_HOSTS=votredomaine.mg,www.votredomaine.mg
CSRF_TRUSTED_ORIGINS=https://votredomaine.mg,https://www.votredomaine.mg
CORS_ALLOWED_ORIGINS=https://votredomaine.mg
FRONTEND_BASE_URL=https://votredomaine.mg
# Optionnel (recommandé) : PostgreSQL
DATABASE_URL=postgres://user:pass@host:5432/ariary
# Optionnel : SMTP réel
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
DEFAULT_FROM_EMAIL=Ariary Numeric <no-reply@votredomaine.mg>
```

### Déploiement local / VPS
```bash
cd /home/aina-ben/Desktop/ariary-numeric
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cd backend
cp ../.env.example ../.env  # puis éditer
python manage.py migrate
python manage.py collectstatic --noinput
DJANGO_SUPERUSER_EMAIL=admin@votredomaine.mg DJANGO_SUPERUSER_PASSWORD='MotDePasseFort!' python manage.py createsuperuser --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120
```

### Déploiement Docker
```bash
cd /home/aina-ben/Desktop/ariary-numeric
cp .env.example .env   # éditer les secrets
docker compose up -d --build
# l'application est disponible sur http://localhost:8001
```

### Plateformes managées (Render / Railway / Fly.io)
- Le `Procfile` et `runtime.txt` sont fournis.
- Définir les variables d'environnement dans le tableau de bord de la plateforme.
- La commande de démarrage est `cd backend && gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`.
- Lancer `python manage.py migrate` et `collectstatic` dans le build command.

### Contrôle de santé
- `GET /healthz/` → `{"status":"ok","database":true}` (503 si la base est indisponible).

### Sauvegarde
```bash
# SQLite
cp backend/db.sqlite3 backups/db-$(date +%F).sqlite3
# PostgreSQL
pg_dump $DATABASE_URL > backups/ariary-$(date +%F).sql
```

### Sécurité en production
- `DJANGO_DEBUG=False` obligatoire.
- `SECRET_KEY` longue et aléatoire (≥ 50 caractères).
- HTTPS activé (redirection automatique + HSTS).
- Aucun secret dans Git (voir `.gitignore`).
- Les documents sont servis par des endpoints authentifiés (pas d'accès public).
- Les transferts réels restent désactivés tant qu'aucun partenaire autorisé n'est intégré.

## Endpoints API
Base: `/api/v1/`
- accounts: register, login, logout, me, guest (compte invité démo)
- wallet: wallet, transactions, transfer, topup-demo
- logistics: shipments
- customs: cases
- blockchain: info, records, verify (empreintes auto des opérations)
- payments: rates, international/estimate, mobile-money/info
- notifications: notifications

## Langues
Interface web disponible en français, malgache (MG) et anglais, basculable en direct (préférence sauvegardée côté compte).

## Mode invité
`POST /api/v1/accounts/guest/` crée un compte de démonstration avec 50 000 MGA préchargés (aucun argent réel). Idéal pour tester sans inscription.
""" 
path: /home/aina-ben/Desktop/ariary-numeric/README.md