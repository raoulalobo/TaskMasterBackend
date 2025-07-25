"""
Configuration de production pour TaskMarket sur Railway
"""

import os
import dj_database_url
from .settings import *

# Configuration de sécurité pour la production
DEBUG = False

# Permettre Railway et autres domaines
ALLOWED_HOSTS = [
    'taskmasterbackend-production.up.railway.app',
    '127.0.0.1',
    'localhost',
    '.railway.app',
    '.up.railway.app'
]

# Configuration de la base de données PostgreSQL pour Railway
DATABASES = {
    'default': dj_database_url.parse(
        os.environ.get('DATABASE_URL', 'sqlite:///db.sqlite3'),
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# Configuration de sécurité
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-*egtedwc+s1w57!y16i_i)_33)wx(apzdohs-h#a*h$fvl4ufi')

# Middleware pour servir les fichiers statiques avec WhiteNoise
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Ajouté pour la production
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Configuration des fichiers statiques pour la production
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Configuration des médias
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Configuration CORS pour permettre le frontend
CORS_ALLOWED_ORIGINS = [
    "https://votre-frontend.vercel.app",  # À remplacer par l'URL de votre frontend
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_ALL_ORIGINS = False  # En production, utiliser une liste spécifique

# Configuration CSRF
CSRF_TRUSTED_ORIGINS = [
    'https://taskmasterbackend-production.up.railway.app',
    'https://*.railway.app',
    'https://*.up.railway.app',
]

# Configuration du Telegram Bot (variables d'environnement)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_WEBHOOK_URL = os.environ.get('TELEGRAM_WEBHOOK_URL', '')

# Configuration des logs pour la production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/tmp/django.log',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Configuration de sécurité supplémentaire
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# En production avec HTTPS
USE_TLS = os.environ.get('USE_TLS', 'False').lower() == 'true'
if USE_TLS:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True