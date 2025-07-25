from django.contrib import admin
from .models import User

# Configuration de l'interface admin pour le modèle User
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Configuration admin pour le modèle User personnalisé"""
    list_display = ['username', 'email', 'user_type', 'first_name', 'last_name', 'created_at']
    list_filter = ['user_type', 'created_at', 'is_active']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']