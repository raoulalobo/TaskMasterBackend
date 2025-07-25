from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Transaction
from properties.models import Property
from decimal import Decimal

User = get_user_model()


class TransactionModelTests(TestCase):
    """Tests pour le modèle Transaction"""
    
    def setUp(self):
        """Configuration des tests"""
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@test.com',
            password='testpass123',
            user_type='landowner'
        )
        
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@test.com',
            password='testpass123',
            user_type='buyer'
        )
        
        self.property = Property.objects.create(
            owner=self.seller,
            title='Test Property',
            description='A test property',
            property_type='house',
            price=Decimal('100000.00'),
            location='Test Location',
            size=Decimal('150.5')
        )
    
    def test_create_transaction(self):
        """Test de création d'une transaction"""
        transaction = Transaction.objects.create(
            property=self.property,
            buyer=self.buyer,
            seller=self.seller,
            agreed_price=Decimal('95000.00')
        )
        self.assertEqual(transaction.property, self.property)
        self.assertEqual(transaction.buyer, self.buyer)
        self.assertEqual(transaction.seller, self.seller)
        self.assertEqual(transaction.status, 'pending')
        self.assertEqual(transaction.agreed_price, Decimal('95000.00'))


class TransactionAPITests(APITestCase):
    """Tests pour l'API Transactions"""
    
    def setUp(self):
        """Configuration des tests"""
        self.seller = User.objects.create_user(
            username='seller',
            email='seller@test.com',  
            password='testpass123',
            user_type='landowner'
        )
        
        self.buyer = User.objects.create_user(
            username='buyer',
            email='buyer@test.com',
            password='testpass123',
            user_type='buyer'
        )
        
        self.property = Property.objects.create(
            owner=self.seller,
            title='Test Property',
            description='A test property',
            property_type='house',
            price=Decimal('100000.00'),
            location='Test Location',
            size=Decimal('150.5')
        )
    
    def test_create_transaction_as_buyer(self):
        """Test de création d'une transaction par un acheteur"""
        self.client.force_authenticate(user=self.buyer)
        url = reverse('transaction-list-create')
        data = {
            'property': self.property.id,
            'agreed_price': '95000.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Vérifier que la transaction a été créée correctement
        transaction = Transaction.objects.get(id=response.data['id'])
        self.assertEqual(transaction.buyer, self.buyer)
        self.assertEqual(transaction.seller, self.seller)
    
    def test_create_transaction_as_landowner_denied(self):
        """Test que les propriétaires ne peuvent pas créer de transactions"""
        self.client.force_authenticate(user=self.seller)
        url = reverse('transaction-list-create')
        data = {
            'property': self.property.id,
            'agreed_price': '95000.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_buyer_cannot_buy_own_property(self):
        """Test qu'un utilisateur ne peut pas acheter sa propre propriété"""
        self.client.force_authenticate(user=self.seller)
        url = reverse('transaction-list-create')
        data = {
            'property': self.property.id,
            'agreed_price': '95000.00'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)