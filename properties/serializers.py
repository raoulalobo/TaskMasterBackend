from rest_framework import serializers
from .models import Property, PropertyImage, PropertyReport, VisitRequest


class PropertyImageSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les images des propriétés"""
    class Meta:
        model = PropertyImage
        fields = ['id', 'image', 'is_main']
        read_only_fields = ['id']


class PropertySerializer(serializers.ModelSerializer):
    """Sérialiseur principal pour les propriétés avec images"""
    images = PropertyImageSerializer(many=True, read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    
    class Meta:
        model = Property
        fields = ['id', 'owner', 'owner_name', 'title', 'description', 'property_type', 
                  'price', 'location', 'size', 'is_available', 'created_at', 'updated_at', 'images']
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at']


class PropertyCreateSerializer(serializers.ModelSerializer):
    """Sérialiseur pour la création de propriétés"""
    class Meta:
        model = Property
        fields = ['title', 'description', 'property_type', 'price', 'location', 'size']
    
    def create(self, validated_data):
        """Le propriétaire sera défini dans la vue"""
        return Property.objects.create(**validated_data)


class PropertyReportSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les signalements de propriétés"""
    reporter_name = serializers.CharField(source='reporter.username', read_only=True)
    
    class Meta:
        model = PropertyReport
        fields = ['id', 'property', 'reporter', 'reporter_name', 'title', 
                  'description', 'status', 'created_at']
        read_only_fields = ['id', 'reporter', 'created_at']
    
    def create(self, validated_data):
        """Le reporter sera défini dans la vue"""
        return PropertyReport.objects.create(**validated_data)


class VisitRequestSerializer(serializers.ModelSerializer):
    """Sérialiseur pour les demandes de visite"""
    requester_name = serializers.CharField(source='requester.username', read_only=True)
    
    class Meta:
        model = VisitRequest
        fields = ['id', 'property', 'requester', 'requester_name', 'title', 
                  'requested_date', 'description', 'status', 'created_at']
        read_only_fields = ['id', 'requester', 'created_at']
    
    def create(self, validated_data):
        """Le requester sera défini dans la vue"""
        return VisitRequest.objects.create(**validated_data)