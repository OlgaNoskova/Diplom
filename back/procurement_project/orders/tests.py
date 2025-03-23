from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Product, Supplier

User = get_user_model()

class UserRegistrationTests(APITestCase):
    def test_register_user(self):
        url = reverse('register')
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'StrongPassword123',
            'role': 'customer'
        }
        response = self.client.post(url, data, format='json')
        # Отключили тротлинг в RegisterView, ожидаем 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='loginuser', password='StrongPassword123', email='login@example.com', role='customer')
    def test_login_user(self):
        url = reverse('login')
        data = {
            'username': 'loginuser',
            'password': 'StrongPassword123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

class ProductListTests(APITestCase):
    def setUp(self):
        # Создаем поставщика для продуктов
        supplier_user = User.objects.create_user(username='supplier1', password='StrongPassword123', email='supplier@example.com', role='supplier')
        self.supplier = Supplier.objects.create(user=supplier_user, company_name='Test Supplier')
        Product.objects.create(supplier=self.supplier, name='Product 1', description='Desc 1', price=10.00, custom_fields={'category': 'Cat1'})
        Product.objects.create(supplier=self.supplier, name='Product 2', description='Desc 2', price=20.00, custom_fields={'category': 'Cat2'})
    def test_get_product_list(self):
        url = reverse('product-list')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 2)

class ThrottlingTests(APITestCase):
    def test_throttling(self):
        url = reverse('product-list')
        # Выполняем 110 запросов, чтобы превысить лимит (100/minute)
        for _ in range(110):
            response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

class ErrorTestTests(APITestCase):
    def test_error_endpoint(self):
        url = reverse('error-test')
        with self.assertRaises(Exception):
            self.client.get(url, format='json')
