from django.db import models
from users.models import User
from properties.models import Property


class Transaction(models.Model):
    """Modèle pour les transactions immobilières"""
    TRANSACTION_STATUS = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
    )
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchases')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sales')
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending')
    agreed_price = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
    
    def __str__(self):
        return f"Transaction for {self.property.title} - {self.status}"