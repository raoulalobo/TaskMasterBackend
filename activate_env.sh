#!/bin/bash
# Script d'activation de l'environnement de développement TaskMarket
# Usage: source activate_env.sh

echo "🚀 Activation de l'environnement TaskMarket Backend..."

# Vérifier si nous sommes dans le bon répertoire
if [ ! -f "manage.py" ]; then
    echo "❌ Erreur: Ce script doit être exécuté depuis le répertoire backend/"
    return 1
fi

# Créer l'environnement virtuel s'il n'existe pas
if [ ! -d "venv" ]; then
    echo "📦 Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
echo "🔧 Activation de l'environnement virtuel..."
source venv/bin/activate

# Vérifier que l'activation a fonctionné
if [ "$VIRTUAL_ENV" != "" ]; then
    echo "✅ Environnement virtuel activé: $VIRTUAL_ENV"
else
    echo "❌ Erreur: L'activation de l'environnement virtuel a échoué"
    return 1
fi

# Installer/mettre à jour les dépendances
echo "📚 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Configurer les variables d'environnement
export DJANGO_SETTINGS_MODULE="taskmarket.settings"
export PYTHONPATH="$PWD:$PYTHONPATH"

# Créer les répertoires nécessaires
mkdir -p media/property_images

echo ""
echo "🎉 Environnement TaskMarket Backend prêt!"
echo "📍 Répertoire: $(pwd)"
echo "🐍 Python: $(python --version)"
echo "📦 Pip: $(pip --version)"

# Vérifier Django
if python -c "import django" 2>/dev/null; then
    echo "🚀 Django: $(python -c 'import django; print(django.get_version())')"
else
    echo "⚠️  Django non disponible - vérifiez l'installation"
fi

echo ""
echo "💡 Commandes disponibles:"
echo "  python manage.py runserver    # Démarrer le serveur (port libre)"
echo "  python manage.py migrate      # Appliquer les migrations"
echo "  python manage.py createsuperuser # Créer un super utilisateur"
echo "  python manage.py runserver 8080 # Démarrer sur le port 8080"
echo ""
echo "✅ Prêt pour le développement Django!"