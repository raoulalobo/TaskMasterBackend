from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .models import User
from .serializers import UserSerializer, UserCreateSerializer


class UserListCreateView(generics.ListCreateAPIView):
    """Vue pour lister les utilisateurs et créer de nouveaux comptes"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.request.method == 'POST':
            # Allow any user to create an account
            permission_classes = [permissions.AllowAny]
        else:
            # Require authentication for listing users
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_serializer_class(self):
        """Utiliser le bon sérialiseur selon l'opération"""
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Vue pour afficher, modifier et supprimer un utilisateur spécifique"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    
class LoginView(generics.GenericAPIView):
    """Vue pour la connexion utilisateur avec création de token"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        """Authentifier l'utilisateur et renvoyer le token"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                # Create or get token
                token, created = Token.objects.get_or_create(user=user)
                return Response({
                    'token': token.key,
                    'user': UserSerializer(user).data
                })
            else:
                return Response({
                    'error': 'Invalid credentials'
                }, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({
                'error': 'Username and password are required'
            }, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(generics.GenericAPIView):
    """Vue pour la déconnexion utilisateur"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Supprimer le token de l'utilisateur pour le déconnecter"""
        try:
            request.user.auth_token.delete()
            return Response({
                'message': 'Logged out successfully'
            })
        except:
            return Response({
                'error': 'Error logging out'
            }, status=status.HTTP_400_BAD_REQUEST)