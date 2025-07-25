from django.contrib import admin
from .models import Transaction


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    """Configuration admin pour les transactions"""
    list_display = ['property', 'buyer', 'seller', 'status', 'agreed_price', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['property__title', 'buyer__username', 'seller__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Transaction Info', {
            'fields': ('property', 'buyer', 'seller', 'agreed_price')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )