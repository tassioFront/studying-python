from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
import json

User = get_user_model()


class TokenAPITestCase(APITestCase):
    """Test cases for JWT token endpoints"""
    
    @classmethod
    def setUpClass(cls):
        """Print test group message"""
        super().setUpClass()
        print("\n" + "="*50)
        print("🧪 RUNNING TESTS FOR JWT TOKEN API")
        print("="*50)
    
    def setUp(self):
        """Set up test data before each test"""
        # Create a test user
        self.user_data = {
            'email': 'testuser@example.com',
            'name': 'Test User',
            'password': 'testpassword123'
        }
        self.user = User.objects.create_user(**self.user_data)
        
        # Define URLs
        self.token_url = reverse('token_obtain_pair')
        self.refresh_url = reverse('token_refresh')

    def test_obtain_token_success(self):
        """Test successful token generation with valid credentials"""
        data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.token_url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Assert tokens are strings and not empty
        self.assertIsInstance(response.data['access'], str)
        self.assertIsInstance(response.data['refresh'], str)
        self.assertTrue(len(response.data['access']) > 0)
        self.assertTrue(len(response.data['refresh']) > 0)

    def test_obtain_token_invalid_credentials(self):
        """Test token generation fails with invalid credentials"""
        data = {
            'email': self.user_data['email'],
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.token_url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_obtain_token_missing_email(self):
        """Test token generation fails when email is missing"""
        data = {
            'password': self.user_data['password']
        }
        
        response = self.client.post(self.token_url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_obtain_token_missing_password(self):
        """Test token generation fails when password is missing"""
        data = {
            'email': self.user_data['email']
        }
        
        response = self.client.post(self.token_url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)

    def test_obtain_token_nonexistent_user(self):
        """Test token generation fails for non-existent user"""
        data = {
            'email': 'nonexistent@example.com',
            'password': 'anypassword'
        }
        
        response = self.client.post(self.token_url, data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_success(self):
        """Test successful token refresh with valid refresh token"""
        # First, get tokens
        login_data = {
            'email': self.user_data['email'],
            'password': self.user_data['password']
        }
        login_response = self.client.post(self.token_url, login_data)
        refresh_token = login_response.data['refresh']
        
        # Now test refresh
        refresh_data = {
            'refresh': refresh_token
        }
        
        response = self.client.post(self.refresh_url, refresh_data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIsInstance(response.data['access'], str)
        self.assertTrue(len(response.data['access']) > 0)

    def test_refresh_token_invalid(self):
        """Test token refresh fails with invalid refresh token"""
        refresh_data = {
            'refresh': 'invalid.refresh.token'
        }
        
        response = self.client.post(self.refresh_url, refresh_data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_missing(self):
        """Test token refresh fails when refresh token is missing"""
        refresh_data = {}
        
        response = self.client.post(self.refresh_url, refresh_data)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('refresh', response.data)

    def test_token_url_get_method_not_allowed(self):
        """Test that GET method is not allowed on token endpoint"""
        response = self.client.get(self.token_url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_refresh_url_get_method_not_allowed(self):
        """Test that GET method is not allowed on refresh endpoint"""
        response = self.client.get(self.refresh_url)
        
        # Assert response
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
