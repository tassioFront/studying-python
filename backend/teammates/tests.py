from django.contrib.auth import get_user_model
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


class UserRegistrationTestCase(APITestCase):
    """Test cases for user registration endpoint"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "=" * 50)
        print("🧪 RUNNING TESTS FOR USER REGISTRATION")
        print("=" * 50)

    def setUp(self):
        """Set up test data before each test"""
        self.register_url = "/api/teammates/register/"
        self.valid_user_data = {
            "email": "testuser@example.com",
            "name": "Test User",
            "password": "securepassword123",
        }

    def test_register_user_success(self):
        """Test successful user registration with valid data"""
        response = self.client.post(self.register_url, self.valid_user_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert user was created in database
        self.assertTrue(
            User.objects.filter(email=self.valid_user_data["email"]).exists()
        )

        # Assert response contains expected fields (but not password)
        self.assertIn("email", response.data)
        self.assertIn("name", response.data)
        self.assertNotIn("password", response.data)

        # Assert correct data
        self.assertEqual(response.data["email"], self.valid_user_data["email"])
        self.assertEqual(response.data["name"], self.valid_user_data["name"])

    def test_register_user_duplicate_email(self):
        """Test registration fails with duplicate email"""
        # Create user first
        User.objects.create_user(**self.valid_user_data)

        # Try to register with same email
        response = self.client.post(self.register_url, self.valid_user_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_missing_email(self):
        """Test registration fails when email is missing"""
        invalid_data = self.valid_user_data.copy()
        del invalid_data["email"]

        response = self.client.post(self.register_url, invalid_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_missing_name(self):
        """Test registration fails when name is missing"""
        invalid_data = self.valid_user_data.copy()
        del invalid_data["name"]

        response = self.client.post(self.register_url, invalid_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_register_user_missing_password(self):
        """Test registration fails when password is missing"""
        invalid_data = self.valid_user_data.copy()
        del invalid_data["password"]

        response = self.client.post(self.register_url, invalid_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_user_invalid_email(self):
        """Test registration fails with invalid email format"""
        invalid_data = self.valid_user_data.copy()
        invalid_data["email"] = "not-an-email"

        response = self.client.post(self.register_url, invalid_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_register_user_short_password(self):
        """Test registration fails with password too short"""
        invalid_data = self.valid_user_data.copy()
        invalid_data["password"] = "123"  # Less than 6 characters

        response = self.client.post(self.register_url, invalid_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_register_user_empty_name(self):
        """Test registration fails with empty name"""
        invalid_data = self.valid_user_data.copy()
        invalid_data["name"] = ""

        response = self.client.post(self.register_url, invalid_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_register_user_get_method_not_allowed(self):
        """Test that GET method is not allowed on registration endpoint"""
        response = self.client.get(self.register_url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_register_superuser_type_blocked(self):
        """Test that superuser type is blocked in registration"""
        superuser_data = {
            "email": "blocked.superuser@example.com",
            "name": "Blocked Superuser",
            "type": "superuser",
            "password": "securepassword123",
        }

        response = self.client.post(self.register_url, superuser_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("type", response.data)
        self.assertIn("Superuser teammates can only be created", str(response.data["type"][0]))

        # Assert user was NOT created in database
        self.assertFalse(
            User.objects.filter(email=superuser_data["email"]).exists()
        )

    def test_register_admin_type_allowed(self):
        """Test that admin type is allowed in registration"""
        admin_data = {
            "email": "admin.teammate@example.com",
            "name": "Admin Teammate",
            "type": "admin",
            "password": "securepassword123",
        }

        response = self.client.post(self.register_url, admin_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["type"], "admin")

        # Assert user was created in database
        self.assertTrue(
            User.objects.filter(email=admin_data["email"], type="admin").exists()
        )


class UserProfileTestCase(APITestCase):
    """Test cases for user profile endpoint"""

    @classmethod
    def setUpClass(cls):
        """Print test group message"""
        super().setUpClass()
        print("\n" + "=" * 50)
        print("🧪 RUNNING TESTS FOR USER PROFILE")
        print("=" * 50)

    def setUp(self):
        """Set up test data before each test"""
        self.profile_url = "/api/teammates/me/"  # Direct URL path

        # Create test user
        self.user_data = {
            "email": "testuser@example.com",
            "name": "Test User",
            "password": "securepassword123",
        }
        self.user = User.objects.create_user(**self.user_data)

        # Generate JWT token for authentication
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)

    def test_get_profile_authenticated_success(self):
        """Test successful profile retrieval with authentication"""
        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.get(self.profile_url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertEqual(response.data["name"], self.user.name)
        self.assertIn("id", response.data)

        # Assert password is not in response
        self.assertNotIn("password", response.data)

    def test_get_profile_unauthenticated_fails(self):
        """Test profile retrieval fails without authentication"""
        # No authentication header
        response = self.client.get(self.profile_url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_invalid_token_fails(self):
        """Test profile retrieval fails with invalid token"""
        # Set invalid authentication header
        self.client.credentials(HTTP_AUTHORIZATION="Bearer invalid.token.here")

        response = self.client.get(self.profile_url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_expired_token_fails(self):
        """Test profile retrieval fails with malformed token"""
        # Set malformed authentication header
        self.client.credentials(HTTP_AUTHORIZATION="Bearer malformed-token")

        response = self.client.get(self.profile_url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_missing_bearer_fails(self):
        """Test profile retrieval fails with missing Bearer prefix"""
        # Set token without Bearer prefix
        self.client.credentials(HTTP_AUTHORIZATION=self.access_token)

        response = self.client.get(self.profile_url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_profile_post_method_not_allowed(self):
        """Test that POST method is not allowed on profile endpoint"""
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.post(self.profile_url, {})

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_get_profile_returns_current_user_only(self):
        """Test that profile endpoint returns current user's data only"""
        # Create another user
        other_user = User.objects.create_user(
            email="other@example.com", name="Other User", password="password123"
        )

        # Authenticate as first user
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

        response = self.client.get(self.profile_url)

        # Assert response returns first user's data, not other user's
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], self.user.email)
        self.assertNotEqual(response.data["email"], other_user.email)


class UserModelTestCase(TestCase):
    """Test cases for User model"""

    @classmethod
    def setUpClass(cls):
        """Print test group message"""
        super().setUpClass()
        print("\n" + "=" * 50)
        print("🧪 RUNNING TESTS FOR USER MODEL")
        print("=" * 50)

    def test_create_user_success(self):
        """Test creating a user with valid data"""
        user_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "securepassword123",
        }

        user = User.objects.create_user(**user_data)

        # Assert user properties
        self.assertEqual(user.email, user_data["email"])
        self.assertEqual(user.name, user_data["name"])
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

        # Assert password is hashed (not plain text)
        self.assertNotEqual(user.password, user_data["password"])
        self.assertTrue(user.check_password(user_data["password"]))

    def test_create_superuser_success(self):
        """Test creating a superuser"""
        user_data = {
            "email": "admin@example.com",
            "name": "Admin User",
            "password": "adminpassword123",
        }

        user = User.objects.create_superuser(**user_data)

        # Assert superuser properties
        self.assertEqual(user.email, user_data["email"])
        self.assertEqual(user.name, user_data["name"])
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_user_no_email_fails(self):
        """Test creating a user without email fails"""
        with self.assertRaises(ValueError):
            User.objects.create_user(email="", name="Test", password="pass123")

    def test_user_string_representation(self):
        """Test user string representation returns email"""
        user = User.objects.create_user(
            email="test@example.com", name="Test User", password="pass123"
        )

        # Assuming you have a __str__ method that returns email
        # If not, you might want to add one to your User model
        self.assertEqual(str(user), user.email)
