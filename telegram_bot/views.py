import json
import logging
import random
import string
from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from telegram import Update, Bot
from telegram.constants import ParseMode

from .models import TelegramUser, TelegramLinkCode, TelegramMessage
from .services import TelegramBotService, PropertyParserService

# Configuration du logging
logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def telegram_webhook(request):
    """
    Endpoint webhook pour recevoir les messages de Telegram
    """
    try:
        # Vérification de la présence du token dans l'URL pour sécurité
        if not settings.TELEGRAM_BOT_TOKEN:
            logger.error("Token Telegram non configuré")
            return HttpResponse(status=500)
        
        # Parsing du JSON reçu de Telegram
        data = json.loads(request.body.decode('utf-8'))
        logger.info(f"Webhook reçu: {data}")
        
        # Création de l'objet Update de python-telegram-bot
        update = Update.de_json(data, Bot(settings.TELEGRAM_BOT_TOKEN))
        
        # Traitement du message via le service
        bot_service = TelegramBotService()
        bot_service.handle_update(update)
        
        return HttpResponse("OK")
        
    except json.JSONDecodeError:
        logger.error("Erreur de parsing JSON dans le webhook")
        return HttpResponse("Invalid JSON", status=400)
    except Exception as e:
        logger.error(f"Erreur dans le webhook: {str(e)}")
        return HttpResponse("Error", status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_link_code(request):
    """
    Génère un code de liaison pour connecter un compte Telegram
    """
    try:
        user = request.user
        
        # Vérification si l'utilisateur a déjà un profil Telegram actif
        try:
            telegram_user = TelegramUser.objects.get(user=user, is_active=True)
            return Response({
                'success': False,
                'message': 'Compte Telegram déjà lié',
                'telegram_username': telegram_user.telegram_username
            })
        except TelegramUser.DoesNotExist:
            pass
        
        # Suppression des anciens codes non utilisés
        TelegramLinkCode.objects.filter(
            user=user,
            is_used=False,
            expires_at__lt=timezone.now()
        ).delete()
        
        # Vérification s'il y a déjà un code valide
        existing_code = TelegramLinkCode.objects.filter(
            user=user,
            is_used=False,
            expires_at__gt=timezone.now()
        ).first()
        
        if existing_code:
            return Response({
                'success': True,
                'code': existing_code.code,
                'expires_at': existing_code.expires_at,
                'message': 'Code existant réutilisé'
            })
        
        # Génération d'un nouveau code
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        expires_at = timezone.now() + timedelta(minutes=settings.TELEGRAM_LINK_CODE_EXPIRY_MINUTES)
        
        # Création du code de liaison
        link_code = TelegramLinkCode.objects.create(
            user=user,
            code=code,
            expires_at=expires_at
        )
        
        return Response({
            'success': True,
            'code': link_code.code,
            'expires_at': link_code.expires_at,
            'bot_username': settings.TELEGRAM_BOT_NAME,
            'instructions': f'Envoyez "/link {code}" au bot @{settings.TELEGRAM_BOT_NAME} sur Telegram'
        })
        
    except Exception as e:
        logger.error(f"Erreur lors de la génération du code: {str(e)}")
        return Response({
            'success': False,
            'message': 'Erreur lors de la génération du code'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_link_status(request):
    """
    Vérifie le statut de liaison du compte Telegram
    """
    try:
        user = request.user
        
        # Vérification du profil Telegram
        try:
            telegram_user = TelegramUser.objects.get(user=user, is_active=True)
            return Response({
                'linked': True,
                'telegram_username': telegram_user.telegram_username,
                'telegram_id': telegram_user.telegram_id,
                'linked_at': telegram_user.created_at
            })
        except TelegramUser.DoesNotExist:
            # Vérification des codes en attente
            pending_code = TelegramLinkCode.objects.filter(
                user=user,
                is_used=False,
                expires_at__gt=timezone.now()
            ).first()
            
            if pending_code:
                return Response({
                    'linked': False,
                    'pending_code': pending_code.code,
                    'expires_at': pending_code.expires_at
                })
            else:
                return Response({
                    'linked': False,
                    'pending_code': None
                })
                
    except Exception as e:
        logger.error(f"Erreur lors de la vérification du statut: {str(e)}")
        return Response({
            'linked': False,
            'error': 'Erreur lors de la vérification'
        }, status=500)