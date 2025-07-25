#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # Détecter automatiquement l'environnement
    # Si on est sur Railway ou en production, utiliser settings_production
    # Sinon utiliser settings par défaut pour le développement
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('DATABASE_URL'):
        settings_module = 'taskmarket.settings_production'
    else:
        settings_module = 'taskmarket.settings'
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()