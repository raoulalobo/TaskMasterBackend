# TaskMaster Backend 🏠

## Description
Backend Django REST API pour TaskMarket - Une plateforme complète de gestion de propriétés immobilières avec intégration bot Telegram.

## 🚀 Fonctionnalités

### 🏠 Gestion des Propriétés
- Création, modification, suppression de propriétés
- Upload multiple d'images pour chaque propriété
- Types de propriétés: Terrain, Maison, Appartement, Commercial
- Système de signalement des propriétés
- Demandes de visite

### 👥 Gestion des Utilisateurs
- Système d'authentification personnalisé
- Types d'utilisateurs: Propriétaire, Acheteur, Administrateur
- Profils utilisateurs avec informations de contact

### 💰 Gestion des Transactions
- Suivi des transactions immobilières
- États de transaction multiples
- Historique complet des transactions

### 🤖 Intégration Bot Telegram
- Bot Telegram intégré pour notifications
- Gestion des conversations Telegram
- Webhooks pour communication en temps réel

## 🛠️ Technologies Utilisées

- **Framework**: Django 5.2.4
- **API**: Django REST Framework 3.16.0
- **Base de données**: SQLite (développement)
- **Upload d'images**: Pillow 11.3.0
- **CORS**: django-cors-headers 4.7.0
- **Bot Telegram**: python-telegram-bot 21.8

## 📋 Prérequis

- Python 3.8+
- pip
- virtualenv (recommandé)

## 🚀 Installation

1. **Cloner le repository**
```bash
git clone https://github.com/raoulalobo/TaskMasterBackend.git
cd TaskMasterBackend
```

2. **Créer un environnement virtuel**
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

4. **Configuration des variables d'environnement**
Créer un fichier `.env` à la racine du projet:
```bash
TELEGRAM_BOT_TOKEN=votre_token_bot_telegram
TELEGRAM_WEBHOOK_URL=votre_url_webhook
TELEGRAM_BOT_NAME=VotreNomBot
```

5. **Migrations de la base de données**
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Créer un superutilisateur**
```bash
python manage.py createsuperuser
```

7. **Lancer le serveur de développement**
```bash
python manage.py runserver
```

## 📁 Structure du Projet

```
TaskMasterBackend/
├── taskmarket/          # Configuration principale Django
│   ├── settings.py      # Paramètres Django
│   ├── urls.py         # URLs principales
│   └── ...
├── users/              # App gestion utilisateurs
│   ├── models.py       # Modèle User personnalisé
│   ├── serializers.py  # Sérialiseurs API
│   └── views.py        # Vues API
├── properties/         # App gestion propriétés
│   ├── models.py       # Modèles Property, PropertyImage, etc.
│   ├── serializers.py  # Sérialiseurs API
│   └── views.py        # Vues API
├── transactions/       # App gestion transactions
├── telegram_bot/       # App bot Telegram
├── requirements.txt    # Dépendances Python
└── manage.py          # Script de gestion Django
```

## 🔌 API Endpoints

### Authentification
- `POST /api/register/` - Inscription utilisateur
- `POST /api/login/` - Connexion utilisateur
- `POST /api/logout/` - Déconnexion

### Propriétés
- `GET /api/properties/` - Liste des propriétés
- `POST /api/properties/` - Créer une propriété
- `GET /api/properties/{id}/` - Détails d'une propriété
- `PUT /api/properties/{id}/` - Modifier une propriété
- `DELETE /api/properties/{id}/` - Supprimer une propriété

### Transactions
- `GET /api/transactions/` - Liste des transactions
- `POST /api/transactions/` - Créer une transaction

### Bot Telegram
- `POST /api/telegram/webhook/` - Webhook bot Telegram

## 🤖 Configuration Bot Telegram

1. Créer un bot via @BotFather sur Telegram
2. Obtenir le token du bot
3. Configurer les variables d'environnement
4. Configurer le webhook pour recevoir les messages

## 🔒 Sécurité

- Authentification par token Django REST Framework
- CORS configuré pour le frontend
- Secret key Django sécurisée (à changer en production)
- Variables d'environnement pour les données sensibles

## 🚀 Déploiement

Pour un déploiement en production:

1. Changer `DEBUG = False` dans settings.py
2. Configurer une base de données PostgreSQL
3. Configurer les fichiers statiques avec un serveur web
4. Utiliser gunicorn comme serveur WSGI
5. Configurer HTTPS pour les webhooks Telegram

## 📝 Licence

Ce projet est sous licence MIT.

## 👨‍💻 Auteur

**Raoul Alobo** - [GitHub](https://github.com/raoulalobo)

---

🎯 *Généré avec Claude Code*