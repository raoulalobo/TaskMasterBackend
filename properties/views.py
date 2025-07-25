from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from .models import Property, PropertyImage, PropertyReport, VisitRequest
from .serializers import (PropertySerializer, PropertyCreateSerializer, PropertyImageSerializer,
                         PropertyReportSerializer, VisitRequestSerializer)
from users.models import User


class PropertyListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des propriétés avec permissions par type d'utilisateur"""
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filtrer les propriétés selon le type d'utilisateur"""
        if self.request.user.is_authenticated:
            if self.request.user.user_type == 'landowner':
                return Property.objects.filter(owner=self.request.user)
            elif self.request.user.user_type == 'buyer':
                return Property.objects.filter(is_available=True)
            elif self.request.user.user_type == 'admin':
                return Property.objects.all()
        return Property.objects.filter(is_available=True)
    
    def get_serializer_class(self):
        """Utiliser le bon sérialiseur selon l'opération"""
        if self.request.method == 'POST':
            return PropertyCreateSerializer
        return PropertySerializer
    
    def perform_create(self, serializer):
        """Seuls les propriétaires peuvent créer des propriétés"""
        if self.request.user.user_type != 'landowner':
            raise permissions.PermissionDenied("Only landowners can create properties.")
        serializer.save(owner=self.request.user)


class PropertyDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour afficher, modifier et supprimer une propriété spécifique"""
    queryset = Property.objects.all()
    serializer_class = PropertySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        """Utiliser le bon sérialiseur selon l'opération"""
        if self.request.method in ['PUT', 'PATCH']:
            return PropertyCreateSerializer
        return PropertySerializer
    
    def perform_update(self, serializer):
        """Seul le propriétaire peut modifier la propriété"""
        property_obj = self.get_object()
        if property_obj.owner != self.request.user and self.request.user.user_type != 'admin':
            raise permissions.PermissionDenied("You don't have permission to update this property.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Seul le propriétaire ou admin peut supprimer la propriété"""
        if instance.owner != self.request.user and self.request.user.user_type != 'admin':
            raise permissions.PermissionDenied("You don't have permission to delete this property.")
        instance.delete()


class PropertyImageView(generics.CreateAPIView):
    """Vue pour ajouter des images aux propriétés"""
    queryset = PropertyImage.objects.all()
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_create(self, serializer):
        """Seul le propriétaire peut ajouter des images"""
        property_id = self.request.data.get('property')
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            raise serializers.ValidationError("Property does not exist.")
            
        if property_obj.owner != self.request.user and self.request.user.user_type != 'admin':
            raise permissions.PermissionDenied("You don't have permission to add images to this property.")
            
        serializer.save(property=property_obj)


class PropertyImageDeleteView(generics.DestroyAPIView):
    """Vue pour supprimer une image spécifique d'une propriété"""
    queryset = PropertyImage.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def perform_destroy(self, instance):
        """Vérifier les permissions avant suppression"""
        if instance.property.owner != self.request.user and self.request.user.user_type != 'admin':
            raise permissions.PermissionDenied("Vous n'avez pas la permission de supprimer cette image.")
        
        # Supprimer le fichier du système de fichiers si nécessaire
        if instance.image and hasattr(instance.image, 'delete'):
            instance.image.delete()
        
        instance.delete()


class PropertyReportListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des signalements de propriétés"""
    serializer_class = PropertyReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les signalements selon le type d'utilisateur"""
        if self.request.user.user_type == 'admin':
            return PropertyReport.objects.all()
        return PropertyReport.objects.filter(reporter=self.request.user)
    
    def perform_create(self, serializer):
        """Validation et création des signalements"""
        property_id = self.request.data.get('property')
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            raise serializers.ValidationError("La propriété spécifiée n'existe pas.")
        
        # Un utilisateur ne peut pas signaler sa propre propriété
        if property_obj.owner == self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez pas signaler votre propre propriété.")
        
        serializer.save(reporter=self.request.user)


class PropertyReportDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour voir, modifier et supprimer un signalement spécifique"""
    serializer_class = PropertyReportSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer selon les permissions"""
        if self.request.user.user_type == 'admin':
            return PropertyReport.objects.all()
        return PropertyReport.objects.filter(reporter=self.request.user)
    
    def perform_update(self, serializer):
        """Contrôler les modifications selon le type d'utilisateur"""
        if self.request.user.user_type != 'admin':
            # Les utilisateurs normaux ne peuvent modifier que leur description
            allowed_fields = {'description'}
            if set(serializer.validated_data.keys()) - allowed_fields:
                raise permissions.PermissionDenied("Vous ne pouvez modifier que la description de votre signalement.")
        
        serializer.save()


class VisitRequestListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des demandes de visite"""
    serializer_class = VisitRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les demandes selon le type d'utilisateur"""
        if self.request.user.user_type == 'admin':
            return VisitRequest.objects.all()
        elif self.request.user.user_type == 'landowner':
            # Demandes pour les propriétés du propriétaire
            return VisitRequest.objects.filter(property__owner=self.request.user)
        else:
            # Demandes faites par l'utilisateur
            return VisitRequest.objects.filter(requester=self.request.user)
    
    def perform_create(self, serializer):
        """Validation et création des demandes de visite"""
        property_id = self.request.data.get('property')
        try:
            property_obj = Property.objects.get(id=property_id)
        except Property.DoesNotExist:
            raise serializers.ValidationError("La propriété spécifiée n'existe pas.")
        
        # Un propriétaire ne peut pas demander une visite de sa propre propriété
        if property_obj.owner == self.request.user:
            raise permissions.PermissionDenied("Vous ne pouvez pas demander une visite de votre propre propriété.")
        
        # Vérifier que la propriété est disponible
        if not property_obj.is_available:
            raise permissions.PermissionDenied("Cette propriété n'est plus disponible.")
        
        serializer.save(requester=self.request.user)


class VisitRequestDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour voir, modifier et supprimer une demande de visite spécifique"""
    serializer_class = VisitRequestSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer selon les permissions"""
        if self.request.user.user_type == 'admin':
            return VisitRequest.objects.all()
        elif self.request.user.user_type == 'landowner':
            return VisitRequest.objects.filter(property__owner=self.request.user)
        else:
            return VisitRequest.objects.filter(requester=self.request.user)
    
    def perform_update(self, serializer):
        """Contrôler les modifications selon le rôle"""
        visit_request = self.get_object()
        
        # Les propriétaires peuvent modifier le statut des demandes pour leurs propriétés
        if visit_request.property.owner == self.request.user:
            allowed_fields = {'status'}
            if set(serializer.validated_data.keys()) - allowed_fields:
                raise permissions.PermissionDenied("Vous ne pouvez modifier que le statut de cette demande.")
        
        # Les demandeurs peuvent modifier leurs propres demandes (sauf le statut)
        elif visit_request.requester == self.request.user:
            if 'status' in serializer.validated_data:
                raise permissions.PermissionDenied("Vous ne pouvez pas modifier le statut de votre demande.")
            allowed_fields = {'requested_date', 'description'}
            if set(serializer.validated_data.keys()) - allowed_fields:
                raise permissions.PermissionDenied("Vous ne pouvez modifier que la date et la description de votre demande.")
        
        # Les admins peuvent tout modifier
        elif self.request.user.user_type != 'admin':
            raise permissions.PermissionDenied("Vous n'avez pas les permissions pour modifier cette demande.")
        
        serializer.save()