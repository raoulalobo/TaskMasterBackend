from django.urls import path
from . import views

# URLs pour l'application telegram_bot
urlpatterns = [
    # Endpoint webhook pour recevoir les messages Telegram
    path('webhook/', views.telegram_webhook, name='telegram_webhook'),
    
    # Endpoint pour générer un code de liaison
    path('generate-link-code/', views.generate_link_code, name='generate_link_code'),
    
    # Endpoint pour vérifier le statut de liaison
    path('link-status/', views.check_link_status, name='check_link_status'),
]