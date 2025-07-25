from django.apps import AppConfig


class TelegramBotConfig(AppConfig):
    """Configuration de l'application Telegram Bot"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_bot'