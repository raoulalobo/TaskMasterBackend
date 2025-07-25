from django.db import models
from users.models import User


class Property(models.Model):
    PROPERTY_TYPES = (
        ('land', 'Land'),
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('commercial', 'Commercial'),
    )
    
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=200)
    size = models.DecimalField(max_digits=10, decimal_places=2, help_text="Size in square meters")
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.owner.username}"


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='property_images/')
    is_main = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Image for {self.property.title}"


class PropertyReport(models.Model):
    """Modèle pour les signalements de propriétés"""
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('reviewed', 'Examiné'),
        ('resolved', 'Résolu'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reports')
    reporter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='property_reports')
    title = models.CharField(max_length=200, help_text="Intitulé du signalement")
    description = models.TextField(help_text="Description détaillée du problème")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Signalement de propriété"
        verbose_name_plural = "Signalements de propriétés"
    
    def __str__(self):
        return f"Signalement: {self.title} - {self.property.title}"


class VisitRequest(models.Model):
    """Modèle pour les demandes de visite"""
    STATUS_CHOICES = (
        ('pending', 'En attente'),
        ('accepted', 'Acceptée'),
        ('rejected', 'Rejetée'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='visit_requests')
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='visit_requests')
    title = models.CharField(max_length=200, default="Demande de visite", help_text="Toujours 'Demande de visite'")
    requested_date = models.DateTimeField(help_text="Date souhaitée pour la visite")
    description = models.TextField(help_text="Commentaires ou informations supplémentaires")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Demande de visite"
        verbose_name_plural = "Demandes de visite"
    
    def __str__(self):
        return f"Visite demandée par {self.requester.username} - {self.property.title}"