import re
import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from telegram import Bot, Update, Message
from telegram.constants import ParseMode

from .models import TelegramUser, TelegramLinkCode, TelegramMessage, TelegramConversation
from properties.models import Property
from users.models import User

logger = logging.getLogger(__name__)


class PropertyParserService:
    """
    Service pour extraire les informations de propriété depuis du texte
    """
    
    def __init__(self):
        # Patterns regex pour extraire les informations
        self.price_patterns = [
            r'prix[:\s]*(\d+(?:\.\d+)?)\s*(?:€|euros?|fcfa)',
            r'(\d+(?:\.\d+)?)\s*(?:€|euros?|fcfa)',
            r'coût[:\s]*(\d+(?:\.\d+)?)',
        ]
        
        self.size_patterns = [
            r'taille[:\s]*(\d+(?:\.\d+)?)\s*(?:m²|m2|mètres?[\s]*carrés?)',
            r'superficie[:\s]*(\d+(?:\.\d+)?)\s*(?:m²|m2)',
            r'(\d+(?:\.\d+)?)\s*(?:m²|m2)',
        ]
        
        self.location_patterns = [
            r'localisation[:\s]*([^\n,]+)',
            r'adresse[:\s]*([^\n,]+)',
            r'situé[\u00e9e]?\s+à[:\s]*([^\n,]+)',
            r'lieu[:\s]*([^\n,]+)',
        ]
        
        self.property_types = {
            'terrain': 'land',
            'maison': 'house',
            'appartement': 'apartment',
            'local commercial': 'commercial',
            'bureau': 'commercial',
            'studio': 'apartment',
            'villa': 'house',
        }
    
    def parse_property_info(self, text: str) -> Dict[str, Any]:
        """
        Extrait les informations de propriété depuis un texte
        """
        text_lower = text.lower()
        result = {
            'title': None,
            'description': text,
            'price': None,
            'size': None,
            'location': None,
            'property_type': 'land',  # par défaut
            'confidence': 0.0
        }
        
        confidence_score = 0.0
        
        # Extraction du prix
        price = self._extract_price(text_lower)
        if price:
            result['price'] = price
            confidence_score += 0.3
        
        # Extraction de la taille
        size = self._extract_size(text_lower)
        if size:
            result['size'] = size
            confidence_score += 0.2
        
        # Extraction de la localisation
        location = self._extract_location(text)
        if location:
            result['location'] = location.strip()
            confidence_score += 0.2
        
        # Détection du type de propriété
        property_type = self._detect_property_type(text_lower)
        if property_type:
            result['property_type'] = property_type
            confidence_score += 0.2
        
        # Génération d'un titre basique
        if result['property_type'] and result['location']:
            type_fr = self._get_type_french(result['property_type'])
            result['title'] = f"{type_fr} à {result['location']}"
            confidence_score += 0.1
        
        result['confidence'] = min(confidence_score, 1.0)
        
        return result
    
    def _extract_price(self, text: str) -> Optional[float]:
        """Extrait le prix depuis le texte"""
        for pattern in self.price_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_size(self, text: str) -> Optional[float]:
        """Extrait la taille depuis le texte"""
        for pattern in self.size_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    def _extract_location(self, text: str) -> Optional[str]:
        """Extrait la localisation depuis le texte"""
        for pattern in self.location_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                location = match.group(1).strip()
                if len(location) > 3:  # Éviter les extractions trop courtes
                    return location
        return None
    
    def _detect_property_type(self, text: str) -> str:
        """Détecte le type de propriété"""
        for type_fr, type_en in self.property_types.items():
            if type_fr in text:
                return type_en
        return 'land'  # par défaut
    
    def _get_type_french(self, property_type: str) -> str:
        """Retourne le nom français du type de propriété"""
        type_map = {
            'land': 'Terrain',
            'house': 'Maison',
            'apartment': 'Appartement',
            'commercial': 'Local commercial'
        }
        return type_map.get(property_type, 'Propriété')


class TelegramBotService:
    """
    Service principal pour gérer les interactions avec le bot Telegram
    """
    
    def __init__(self):
        self.bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
        self.parser = PropertyParserService()
    
    def handle_update(self, update: Update):
        """
        Traite une mise à jour reçue de Telegram
        """
        try:
            if update.message:
                self._handle_message(update.message)
            elif update.edited_message:
                self._handle_message(update.edited_message)
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement de l'update: {str(e)}")
    
    def _handle_message(self, message: Message):
        """
        Traite un message reçu
        """
        try:
            telegram_id = message.from_user.id
            
            # Log du message
            self._log_message(message)
            
            # Vérifier d'abord l'état de conversation
            conversation = self._get_or_create_conversation(telegram_id)
            
            # Traitement des commandes
            if message.text and message.text.startswith('/'):
                self._handle_command(message)
            elif conversation.state == 'awaiting_property_confirmation':
                self._handle_property_confirmation(message, conversation)
            elif conversation.state == 'awaiting_images':
                self._handle_images_upload(message, conversation)
            elif conversation.state == 'awaiting_image_selection':
                self._handle_image_selection(message, conversation)
            elif message.photo:
                # Traitement des photos envoyées hors contexte
                self._handle_standalone_photo(message)
            else:
                # Traitement des messages normaux (potentielles propriétés)
                self._handle_property_message(message)
                
        except Exception as e:
            logger.error(f"Erreur lors du traitement du message: {str(e)}")
            self._send_error_message(message.chat_id)
    
    def _handle_command(self, message: Message):
        """
        Traite les commandes du bot
        """
        command_text = message.text
        telegram_id = message.from_user.id
        
        if command_text.startswith('/start'):
            self._handle_start_command(message)
        elif command_text.startswith('/help'):
            self._handle_help_command(message)
        elif command_text.startswith('/link'):
            self._handle_link_command(message)
        elif command_text.startswith('/add'):
            self._handle_add_command(message)
        elif command_text.startswith('/list'):
            self._handle_list_command(message)
        elif command_text.startswith('/done'):
            self._handle_done_command(message)
        elif command_text.startswith('/cancel'):
            self._handle_cancel_command(message)
        elif command_text.startswith('/status'):
            self._handle_status_command(message)
        elif command_text.startswith('/addimage'):
            self._handle_addimage_command(message)
        else:
            self._send_unknown_command_message(message.chat_id)
    
    # [Méthodes de gestion des commandes - implémentation complète disponible dans le fichier original]
    
    def _get_telegram_user(self, telegram_id: int) -> Optional[TelegramUser]:
        """Récupère l'utilisateur Telegram lié"""
        try:
            return TelegramUser.objects.get(telegram_id=telegram_id, is_active=True)
        except TelegramUser.DoesNotExist:
            return None
    
    def _send_not_linked_message(self, chat_id: int):
        """Envoie un message pour compte non lié"""
        self.bot.send_message(
            chat_id=chat_id,
            text="❌ Compte non lié.\n\nConnectez-vous sur TaskMarket web et utilisez /link avec votre code de liaison."
        )