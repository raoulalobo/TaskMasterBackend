from django.contrib import admin
from .models import TelegramUser, TelegramLinkCode, TelegramMessage, TelegramConversation


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    """Configuration admin pour les utilisateurs Telegram"""
    list_display = ['user', 'telegram_username', 'telegram_id', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'telegram_username', 'telegram_first_name', 'telegram_last_name']
    ordering = ['-created_at']
    readonly_fields = ['telegram_id', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Utilisateur TaskMarket', {
            'fields': ('user',)
        }),
        ('Informations Telegram', {
            'fields': ('telegram_id', 'telegram_username', 'telegram_first_name', 'telegram_last_name')
        }),
        ('Statut', {
            'fields': ('is_active',)
        }),
        ('Horodatage', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(TelegramLinkCode)
class TelegramLinkCodeAdmin(admin.ModelAdmin):
    """Configuration admin pour les codes de liaison"""
    list_display = ['code', 'user', 'is_used', 'expires_at', 'created_at']
    list_filter = ['is_used', 'expires_at', 'created_at']
    search_fields = ['code', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['code', 'created_at']
    
    def has_change_permission(self, request, obj=None):
        # Empêcher la modification des codes utilisés
        if obj and obj.is_used:
            return False
        return super().has_change_permission(request, obj)


@admin.register(TelegramMessage)
class TelegramMessageAdmin(admin.ModelAdmin):
    """Configuration admin pour les messages Telegram"""
    list_display = ['telegram_user', 'message_type', 'content_preview', 'processed', 'created_at']
    list_filter = ['message_type', 'processed', 'created_at']
    search_fields = ['content', 'telegram_user__user__username']
    ordering = ['-created_at']
    readonly_fields = ['telegram_user', 'message_type', 'content', 'telegram_message_id', 'created_at']
    
    def content_preview(self, obj):
        """Aperçu du contenu du message"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Aperçu du contenu'
    
    def has_add_permission(self, request):
        # Les messages sont créés automatiquement
        return False
    
    def has_change_permission(self, request, obj=None):
        # Permettre seulement de marquer comme traité
        return True
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # En mode édition
            return ['telegram_user', 'message_type', 'content', 'telegram_message_id', 'created_at']
        return self.readonly_fields


@admin.register(TelegramConversation)
class TelegramConversationAdmin(admin.ModelAdmin):
    """Configuration admin pour les conversations Telegram"""
    list_display = ['telegram_user', 'state', 'context_preview', 'updated_at']
    list_filter = ['state', 'updated_at']
    search_fields = ['telegram_user__user__username', 'telegram_user__telegram_username']
    ordering = ['-updated_at']
    readonly_fields = ['telegram_user', 'updated_at']
    
    def context_preview(self, obj):
        """Aperçu des données de contexte"""
        if obj.context_data:
            keys = list(obj.context_data.keys())
            if keys:
                return f"{len(keys)} clés: {', '.join(keys[:3])}{'...' if len(keys) > 3 else ''}"
        return 'Vide'
    context_preview.short_description = 'Contexte'
    
    fieldsets = (
        ('Utilisateur', {
            'fields': ('telegram_user',)
        }),
        ('Conversation', {
            'fields': ('state', 'context_data')
        }),
        ('Horodatage', {
            'fields': ('updated_at',),
            'classes': ('collapse',)
        })
    )