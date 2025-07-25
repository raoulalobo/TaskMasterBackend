from django.db import models
from django.conf import settings
from django.utils import timezone


class TelegramUser(models.Model):
    """
    Modèle pour lier les utilisateurs Telegram aux comptes TaskMarket
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='telegram_profile',
        verbose_name="Utilisateur"
    )
    telegram_id = models.BigIntegerField(
        unique=True,
        verbose_name="ID Telegram"
    )
    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nom d'utilisateur Telegram"
    )
    telegram_first_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Prénom Telegram"
    )
    telegram_last_name = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Nom Telegram"
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification"
    )
    
    class Meta:
        verbose_name = "Utilisateur Telegram"
        verbose_name_plural = "Utilisateurs Telegram"
        db_table = 'telegram_users'
    
    def __str__(self):
        return f"{self.user.username} (@{self.telegram_username or self.telegram_id})"


class TelegramLinkCode(models.Model):
    """
    Codes temporaires pour lier les comptes Telegram aux comptes TaskMarket
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="Code de liaison"
    )
    telegram_id = models.BigIntegerField(
        null=True,
        blank=True,
        verbose_name="ID Telegram"
    )
    is_used = models.BooleanField(
        default=False,
        verbose_name="Utilisé"
    )
    expires_at = models.DateTimeField(
        verbose_name="Expire le"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    
    class Meta:
        verbose_name = "Code de liaison Telegram"
        verbose_name_plural = "Codes de liaison Telegram"
        db_table = 'telegram_link_codes'
    
    def __str__(self):
        return f"Code {self.code} pour {self.user.username}"
    
    def is_expired(self):
        """Vérifie si le code a expiré"""
        return timezone.now() > self.expires_at


class TelegramMessage(models.Model):
    """
    Log des messages reçus via Telegram pour debug et historique
    """
    MESSAGE_TYPE_CHOICES = [
        ('text', 'Texte'),
        ('photo', 'Photo'),
        ('command', 'Commande'),
        ('other', 'Autre'),
    ]
    
    telegram_user = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name="Utilisateur Telegram"
    )
    message_type = models.CharField(
        max_length=20,
        choices=MESSAGE_TYPE_CHOICES,
        default='text',
        verbose_name="Type de message"
    )
    content = models.TextField(
        verbose_name="Contenu"
    )
    telegram_message_id = models.BigIntegerField(
        verbose_name="ID Message Telegram"
    )
    processed = models.BooleanField(
        default=False,
        verbose_name="Traité"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de réception"
    )
    
    class Meta:
        verbose_name = "Message Telegram"
        verbose_name_plural = "Messages Telegram"
        db_table = 'telegram_messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message de {self.telegram_user} - {self.message_type} ({self.created_at})"


class TelegramConversation(models.Model):
    """
    Modèle pour gérer les états de conversation du bot
    """
    STATE_CHOICES = [
        ('idle', 'Inactif'),
        ('awaiting_property_confirmation', 'En attente de confirmation de propriété'),
        ('awaiting_property_details', 'En attente de détails de propriété'),
        ('awaiting_images', 'En attente d\'images de propriété'),
        ('awaiting_image_selection', 'En attente de sélection d\'image principale'),
    ]
    
    telegram_user = models.OneToOneField(
        TelegramUser,
        on_delete=models.CASCADE,
        related_name='conversation',
        verbose_name="Utilisateur Telegram"
    )
    state = models.CharField(
        max_length=50,
        choices=STATE_CHOICES,
        default='idle',
        verbose_name="État de la conversation"
    )
    context_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Données de contexte"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Dernière mise à jour"
    )
    
    class Meta:
        verbose_name = "Conversation Telegram"
        verbose_name_plural = "Conversations Telegram"
        db_table = 'telegram_conversations'
    
    def __str__(self):
        return f"Conversation {self.telegram_user} - {self.state}"