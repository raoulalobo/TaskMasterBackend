from rest_framework import serializers
from .models import Transaction
from properties.models import Property
from users.models import User


class TransactionSerializer(serializers.ModelSerializer):
    """Sérialiseur principal pour les transactions"""
    property_title = serializers.CharField(source='property.title', read_only=True)
    buyer_name = serializers.CharField(source='buyer.username', read_only=True)
    seller_name = serializers.CharField(source='seller.username', read_only=True)
    
    class Meta:
        model = Transaction
        fields = ['id', 'property', 'property_title', 'buyer', 'buyer_name', 'seller', 'seller_name', 
                  'status', 'agreed_price', 'created_at', 'updated_at']
        read_only_fields = ['id', 'buyer', 'seller', 'created_at', 'updated_at']


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création de transactions"""
    class Meta:
        model = Transaction
        fields = ['property', 'agreed_price']
    
    def validate_property(self, value):
        """Vérifier que la propriété est disponible"""
        if not value.is_available:
            raise serializers.ValidationError("This property is not available for purchase.")
        return value
    
    def create(self, validated_data):
        """Créer une transaction avec le vendeur automatiquement défini"""
        # L'acheteur sera défini dans la vue
        # Le vendeur est le propriétaire de la propriété
        property_obj = validated_data['property']
        validated_data['seller'] = property_obj.owner
        return Transaction.objects.create(**validated_data)