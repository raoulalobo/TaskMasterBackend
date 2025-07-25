from django.contrib import admin
from .models import Property, PropertyImage, PropertyReport, VisitRequest


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    """Configuration admin pour les propriétés"""
    list_display = ['title', 'owner', 'property_type', 'price', 'location', 'is_available', 'created_at']
    list_filter = ['property_type', 'is_available', 'created_at']
    search_fields = ['title', 'location', 'owner__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    """Configuration admin pour les images de propriétés"""
    list_display = ['property', 'is_main', 'created_at']
    list_filter = ['is_main', 'created_at']
    search_fields = ['property__title']
    ordering = ['-created_at']


@admin.register(PropertyReport)
class PropertyReportAdmin(admin.ModelAdmin):
    """Configuration admin pour les signalements"""
    list_display = ['title', 'property', 'reporter', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['title', 'property__title', 'reporter__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(VisitRequest)
class VisitRequestAdmin(admin.ModelAdmin):
    """Configuration admin pour les demandes de visite"""
    list_display = ['property', 'requester', 'requested_date', 'status', 'created_at']
    list_filter = ['status', 'requested_date', 'created_at']
    search_fields = ['property__title', 'requester__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']