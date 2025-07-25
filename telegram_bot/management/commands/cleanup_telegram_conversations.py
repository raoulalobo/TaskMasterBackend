from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from telegram_bot.models import TelegramConversation, TelegramLinkCode


class Command(BaseCommand):
    """Commande pour nettoyer les conversations et codes Telegram expirés"""
    help = 'Nettoie les conversations Telegram inactives et les codes de liaison expirés'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--conversation-timeout',
            type=int,
            default=24,
            help='Timeout en heures pour les conversations inactives (défaut: 24h)'
        )
        
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mode simulation - affiche ce qui serait supprimé sans le faire'
        )
    
    def handle(self, *args, **options):
        """Exécute le nettoyage"""
        timeout_hours = options['conversation_timeout']
        dry_run = options['dry_run']
        
        # Calcul de la date limite
        timeout_date = timezone.now() - timedelta(hours=timeout_hours)
        
        # Nettoyage des conversations inactives
        inactive_conversations = TelegramConversation.objects.filter(
            state__ne='idle',
            updated_at__lt=timeout_date
        )
        
        conv_count = inactive_conversations.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] {conv_count} conversations seraient réinitialisées'
                )
            )
        else:
            # Réinitialiser les conversations inactives
            inactive_conversations.update(
                state='idle',
                context_data={}
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'{conv_count} conversations inactives réinitialisées'
                )
            )
        
        # Nettoyage des codes de liaison expirés
        expired_codes = TelegramLinkCode.objects.filter(
            expires_at__lt=timezone.now(),
            is_used=False
        )
        
        codes_count = expired_codes.count()
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f'[DRY RUN] {codes_count} codes de liaison expirés seraient supprimés'
                )
            )
        else:
            expired_codes.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'{codes_count} codes de liaison expirés supprimés'
                )
            )
        
        if not dry_run:
            self.stdout.write(
                self.style.SUCCESS('Nettoyage terminé avec succès !')
            )