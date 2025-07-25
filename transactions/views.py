from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from .models import Transaction
from .serializers import TransactionSerializer, TransactionCreateSerializer
from properties.models import Property


class TransactionListCreateView(generics.ListCreateAPIView):
    """Vue pour lister et créer des transactions"""
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer les transactions selon le type d'utilisateur"""
        user = self.request.user
        if user.user_type == 'landowner':
            # Propriétaires voient leurs ventes
            return Transaction.objects.filter(seller=user)
        elif user.user_type == 'buyer':
            # Acheteurs voient leurs achats
            return Transaction.objects.filter(buyer=user)
        elif user.user_type == 'admin':
            # Admins voient toutes les transactions
            return Transaction.objects.all()
        return Transaction.objects.none()
    
    def get_serializer_class(self):
        """Utiliser le bon sérialiseur selon l'opération"""
        if self.request.method == 'POST':
            return TransactionCreateSerializer
        return TransactionSerializer
    
    def perform_create(self, serializer):
        """Seuls les acheteurs peuvent initier des transactions"""
        if self.request.user.user_type != 'buyer':
            raise permissions.PermissionDenied("Only buyers can initiate transactions.")
        
        # Vérifier si l'acheteur a déjà une transaction en cours pour cette propriété
        property_obj = serializer.validated_data['property']
        existing_transaction = Transaction.objects.filter(
            property=property_obj,
            buyer=self.request.user,
            status='pending'
        ).exists()
        
        if existing_transaction:
            raise serializers.ValidationError("You already have a pending transaction for this property.")
        
        # Vérifier que l'acheteur ne tente pas d'acheter sa propre propriété
        if property_obj.owner == self.request.user:
            raise permissions.PermissionDenied("You cannot buy your own property.")
            
        serializer.save(buyer=self.request.user)


class TransactionDetailView(generics.RetrieveUpdateAPIView):
    """Vue pour afficher et modifier une transaction spécifique"""
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filtrer selon les permissions"""
        user = self.request.user
        if user.user_type == 'admin':
            return Transaction.objects.all()
        # Seuls les participants peuvent voir la transaction
        return Transaction.objects.filter(
            models.Q(buyer=user) | models.Q(seller=user)
        )
    
    def perform_update(self, serializer):
        """Contrôler les modifications selon le rôle"""
        transaction = self.get_object()
        user = self.request.user
        
        if user.user_type == 'admin':
            # Admin peut tout modifier
            serializer.save()
        elif user == transaction.buyer:
            # Acheteur peut seulement annuler (rejected)
            if 'status' in serializer.validated_data:
                allowed_statuses = ['rejected']
                if serializer.validated_data['status'] not in allowed_statuses:
                    raise permissions.PermissionDenied("Buyers can only reject transactions.")
            serializer.save()
        elif user == transaction.seller:
            # Vendeur peut accepter, rejeter ou marquer comme complété
            if 'status' in serializer.validated_data:
                allowed_statuses = ['accepted', 'rejected', 'completed']
                if serializer.validated_data['status'] not in allowed_statuses:
                    raise permissions.PermissionDenied("Invalid status change for seller.")
            serializer.save()
        else:
            raise permissions.PermissionDenied("You don't have permission to update this transaction.")