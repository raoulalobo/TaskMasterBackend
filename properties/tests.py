from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from .models import Property, PropertyImage, PropertyReport, VisitRequest

User = get_user_model()


class PropertyModelTests(TestCase):
    """Tests pour le modèle Property"""
    
    def setUp(self):
        """Configuration des tests"""
        self.user = User.objects.create_user(
            username='landowner',
            email='landowner@test.com',
            password='testpass123',
            user_type='landowner'
        )
    
    def test_create_property(self):
        """Test de création d'une propriété"""
        property_obj = Property.objects.create(
            owner=self.user,
            title='Test Property',
            description='A test property',
            property_type='house',
            price=100000.00,
            location='Test Location',
            size=150.5
        )
        self.assertEqual(property_obj.title, 'Test Property')
        self.assertEqual(property_obj.owner, self.user)
        self.assertTrue(property_obj.is_available)


class PropertyAPITests(APITestCase):
    """Tests pour l'API Properties"""
    
    def setUp(self):
        """Configuration des tests"""
        self.landowner = User.objects.create_user(
            username='landowner',
            email='landowner@test.com',
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
            owner=self.landowner,
            title='Test Property',
            description='A test property',
            property_type='house',
            price=100000.00,
            location='Test Location',
            size=150.5
        )
    
    def test_create_property_as_landowner(self):
        """Test de création d'une propriété par un propriétaire"""
        self.client.force_authenticate(user=self.landowner)
        url = reverse('property-list-create')
        data = {
            'title': 'New Property',
            'description': 'A new property',
            'property_type': 'apartment',
            'price': 75000.00,
            'location': 'New Location',
            'size': 80.0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_property_as_buyer_denied(self):
        """Test que les acheteurs ne peuvent pas créer de propriétés"""
        self.client.force_authenticate(user=self.buyer)
        url = reverse('property-list-create')
        data = {
            'title': 'New Property',
            'description': 'A new property',
            'property_type': 'apartment',
            'price': 75000.00,
            'location': 'New Location',
            'size': 80.0
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_properties(self):
        """Test de listage des propriétés"""
        url = reverse('property-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)