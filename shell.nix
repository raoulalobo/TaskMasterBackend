# Configuration Nix pour l'environnement de développement TaskMarket Backend
# Usage: nix-shell pour entrer dans l'environnement de développement

{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  name = "taskmarket-backend-env";
  
  buildInputs = with pkgs; [
    # Python 3.12 et outils de base
    python312
    python312Packages.pip
    python312Packages.setuptools
    python312Packages.wheel
    
    # Dépendances système requises pour les packages Python
    libffi
    openssl
    zlib
    libjpeg
    libpng
    freetype
    postgresql
    
    # Outils de développement
    git
    curl
    
    # Dépendances Python pour Django et TaskMarket
    python312Packages.django
    python312Packages.djangorestframework
    python312Packages.django-cors-headers
    python312Packages.pillow
    python312Packages.gunicorn
    python312Packages.whitenoise
    python312Packages.psycopg2
  ];
  
  shellHook = ''
    echo "🚀 Environnement TaskMarket Backend activé!"
    echo "📍 Répertoire: $(pwd)"
    echo "🐍 Python: $(python --version)"
    echo "📦 Django: $(python -c 'import django; print(django.get_version())')"
    echo ""
    echo "💡 Commandes disponibles:"
    echo "  python manage.py runserver    # Démarrer le serveur de développement"
    echo "  python manage.py migrate      # Appliquer les migrations"
    echo "  python manage.py createsuperuser # Créer un super utilisateur"
    echo ""
    
    # Configurer l'environnement Python
    export PYTHONPATH="$PWD:$PYTHONPATH"
    export DJANGO_SETTINGS_MODULE="taskmarket.settings"
    
    # Créer le répertoire de médias si nécessaire
    mkdir -p media/property_images
    
    # Message de bienvenue
    echo "✅ Environnement prêt pour le développement Django!"
  '';
  
  # Variables d'environnement
  DJANGO_SETTINGS_MODULE = "taskmarket.settings";
  PYTHONPATH = ".";
}