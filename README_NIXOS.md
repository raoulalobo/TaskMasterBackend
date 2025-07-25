# 🐧 Guide NixOS pour TaskMarket Backend

Ce guide explique comment résoudre l'erreur `externally-managed-environment` sur NixOS et configurer correctement l'environnement de développement Django.

## ❌ Problème rencontré

```
× This environment is externally managed
╰─> This command has been disabled as it tries to modify the immutable
    `/nix/store` filesystem.
```

## ✅ Solutions disponibles

### Solution 1: Script d'activation automatique (Recommandé)

**Usage simple :**
```bash
cd /path/to/taskmarket/backend
source activate_env.sh
```

Le script `activate_env.sh` :
- ✅ Crée automatiquement l'environnement virtuel si nécessaire
- ✅ Active l'environnement virtuel correctement
- ✅ Installe toutes les dépendances Django
- ✅ Configure les variables d'environnement
- ✅ Vérifie que tout fonctionne

### Solution 2: Commandes manuelles

Si vous préférez le contrôle manuel :

```bash
# 1. Créer l'environnement virtuel
python3 -m venv venv

# 2. Activer l'environnement (IMPORTANT: à faire avant chaque session)
source venv/bin/activate

# 3. Installer les dépendances
pip install --upgrade pip
pip install -r requirements.txt

# 4. Vérifier que Django fonctionne
python manage.py check
```

### Solution 3: Environnement Nix natif (Si Nix est installé)

Si vous avez Nix disponible :

```bash
# Entrer dans l'environnement Nix
nix-shell

# Ou avec le shell.nix fourni
nix-shell shell.nix
```

## 🚀 Commandes Django disponibles

Une fois l'environnement activé :

```bash
# Vérifier la configuration
python manage.py check

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Démarrer le serveur de développement
python manage.py runserver

# Démarrer sur un port spécifique
python manage.py runserver 8080
```

## 🔧 Dépannage

### Erreur persistante `externally-managed-environment`

**Cause :** Vous essayez d'utiliser pip en dehors de l'environnement virtuel.

**Solution :** Toujours activer l'environnement virtuel d'abord :
```bash
source venv/bin/activate  # OBLIGATOIRE avant toute commande pip
pip install package_name
```

### Vérifier l'activation de l'environnement

```bash
# Vérifier que l'environnement est activé
echo $VIRTUAL_ENV
# Doit afficher: /path/to/backend/venv

# Vérifier la version de Python utilisée
which python
# Doit afficher: /path/to/backend/venv/bin/python
```

### Port déjà utilisé

Si le port 8000 est occupé :
```bash
# Utiliser un autre port
python manage.py runserver 8080

# Ou trouver le processus qui utilise le port
lsof -i :8000
```

## 📁 Structure des fichiers

```
backend/
├── activate_env.sh      # Script d'activation automatique
├── shell.nix           # Configuration Nix (si disponible)
├── venv/               # Environnement virtuel Python
├── requirements.txt    # Dépendances Python
├── manage.py          # Script Django principal
└── README_NIXOS.md    # Ce guide
```

## 💡 Conseils pour NixOS

1. **Toujours utiliser l'environnement virtuel** - Ne jamais installer de packages Python globalement
2. **Script d'activation** - Utiliser `source activate_env.sh` pour automatiser le processus
3. **Variables d'environnement** - Le script configure automatiquement `DJANGO_SETTINGS_MODULE`
4. **Persistance** - L'environnement virtuel est créé une seule fois, puis réutilisé

## 🎯 Commande rapide pour démarrer

```bash
# Démarrage complet en une commande
cd /path/to/taskmarket/backend && source activate_env.sh && python manage.py runserver 8080
```

---

**✅ Avec cette configuration, l'erreur `externally-managed-environment` est complètement résolue !**