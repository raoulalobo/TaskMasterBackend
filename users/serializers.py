from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les données utilisateur (lecture)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'user_type', 'phone_number', 'address']
        read_only_fields = ['id']


class UserCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création d'utilisateurs"""
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'user_type', 'phone_number', 'address']
    
    def create(self, validated_data):
        """Créer un utilisateur avec mot de passe hashé"""
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user