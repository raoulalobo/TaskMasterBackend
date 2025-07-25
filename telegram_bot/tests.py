from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import TelegramUser, TelegramLinkCode, TelegramMessage, TelegramConversation
from .services import PropertyParserService

User = get_user_model()


class TelegramModelTests(TestCase):
    """Tests pour les modèles Telegram"""
    
    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='landowner'
        )
    
    def test_create_telegram_user(self):
        """Test de création d'un utilisateur Telegram"""
        telegram_user = TelegramUser.objects.create(
            user=self.user,
            telegram_id=123456789,
            telegram_username='testuser_tg',
            telegram_first_name='Test',
            telegram_last_name='User'
        )
        
        self.assertEqual(telegram_user.user, self.user)
        self.assertEqual(telegram_user.telegram_id, 123456789)
        self.assertEqual(telegram_user.telegram_username, 'testuser_tg')
        self.assertTrue(telegram_user.is_active)
    
    def test_create_link_code(self):
        """Test de création d'un code de liaison"""
        expires_at = timezone.now() + timedelta(minutes=30)
        link_code = TelegramLinkCode.objects.create(
            user=self.user,
            code='ABC12345',
            expires_at=expires_at
        )
        
        self.assertEqual(link_code.user, self.user)
        self.assertEqual(link_code.code, 'ABC12345')
        self.assertFalse(link_code.is_used)
        self.assertFalse(link_code.is_expired())
    
    def test_link_code_expiry(self):
        """Test de l'expiration d'un code de liaison"""
        expires_at = timezone.now() - timedelta(minutes=5)  # Expiré
        link_code = TelegramLinkCode.objects.create(
            user=self.user,
            code='EXPIRED1',
            expires_at=expires_at
        )
        
        self.assertTrue(link_code.is_expired())


class PropertyParserTests(TestCase):
    """Tests pour le service de parsing des propriétés"""
    
    def setUp(self):
        """Configuration des tests"""
        self.parser = PropertyParserService()
    
    def test_parse_complete_property(self):
        """Test de parsing d'une propriété complète"""
        text = "Terrain de 500m² à Yaoundé, prix 25000€. Bien situé dans un quartier calme."
        
        result = self.parser.parse_property_info(text)
        
        self.assertEqual(result['property_type'], 'land')
        self.assertEqual(result['price'], 25000.0)
        self.assertEqual(result['size'], 500.0)
        self.assertEqual(result['location'], 'Yaoundé')
        self.assertIn('Terrain', result['title'])
        self.assertGreater(result['confidence'], 0.5)
    
    def test_parse_house_property(self):
        """Test de parsing d'une maison"""
        text = "Belle maison 3 chambres à Douala, 80000 euros, 150m²"
        
        result = self.parser.parse_property_info(text)
        
        self.assertEqual(result['property_type'], 'house')
        self.assertEqual(result['price'], 80000.0)
        self.assertEqual(result['size'], 150.0)
        self.assertEqual(result['location'], 'Douala')
        self.assertIn('Maison', result['title'])
    
    def test_parse_incomplete_property(self):
        """Test de parsing d'une propriété incomplète"""
        text = "Joli terrain pas cher"
        
        result = self.parser.parse_property_info(text)
        
        self.assertIsNone(result['price'])
        self.assertIsNone(result['size'])
        self.assertIsNone(result['location'])
        self.assertLess(result['confidence'], 0.3)


class TelegramAPITests(APITestCase):
    """Tests pour l'API Telegram"""
    
    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='landowner'
        )
    
    def test_generate_link_code_authenticated(self):
        """Test de génération de code de liaison pour utilisateur authentifié"""
        self.client.force_authenticate(user=self.user)
        url = reverse('generate_link_code')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('code', response.data)
        self.assertIn('expires_at', response.data)
        
        # Vérifier que le code a été créé en base
        self.assertTrue(
            TelegramLinkCode.objects.filter(
                user=self.user,
                code=response.data['code']
            ).exists()
        )
    
    def test_generate_link_code_unauthenticated(self):
        """Test de génération de code sans authentification"""
        url = reverse('generate_link_code')
        
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_check_link_status_unlinked(self):
        """Test de vérification du statut pour un compte non lié"""
        self.client.force_authenticate(user=self.user)
        url = reverse('check_link_status')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['linked'])
    
    def test_check_link_status_linked(self):
        """Test de vérification du statut pour un compte lié"""
        # Créer un utilisateur Telegram lié
        telegram_user = TelegramUser.objects.create(
            user=self.user,
            telegram_id=123456789,
            telegram_username='testuser_tg'
        )
        
        self.client.force_authenticate(user=self.user)
        url = reverse('check_link_status')
        
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['linked'])
        self.assertEqual(response.data['telegram_username'], 'testuser_tg')
        self.assertEqual(response.data['telegram_id'], 123456789)