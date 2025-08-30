from django.test import TestCase

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from teammates.models import User as Teammate

from .models import User


class UserModelTestCase(TestCase):
    """Test cases for User model"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "=" * 50)
        print("🧪 RUNNING TESTS FOR USER MODEL")
        print("=" * 50)

    def test_create_user_success(self):
        """Test creating a user with valid data"""
        user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890",
        }

        user = User.objects.create(**user_data)

        # Assert user properties
        self.assertEqual(user.email, user_data["email"])
        self.assertEqual(user.first_name, user_data["first_name"])
        self.assertEqual(user.last_name, user_data["last_name"])
        self.assertEqual(user.phone, user_data["phone"])
        self.assertEqual(user.status, User.ACTIVE)
        self.assertTrue(user.email_notifications)
        self.assertTrue(user.is_active)

    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create(
            email="test@example.com", first_name="John", last_name="Doe"
        )
        expected_str = "John Doe (test@example.com)"
        self.assertEqual(str(user), expected_str)

    def test_get_full_name(self):
        """Test get_full_name method"""
        user = User.objects.create(
            email="test@example.com", first_name="John", last_name="Doe"
        )
        self.assertEqual(user.get_full_name(), "John Doe")

    def test_get_short_name(self):
        """Test get_short_name method"""
        user = User.objects.create(
            email="test@example.com", first_name="John", last_name="Doe"
        )
        self.assertEqual(user.get_short_name(), "John")


class UserAPITestCase(APITestCase):
    """Test cases for User API endpoints"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "=" * 50)
        print("🧪 RUNNING TESTS FOR USER API")
        print("=" * 50)

    def setUp(self):
        """Set up test data before each test"""
        self.users_url = "/api/users/"
        self.valid_user_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890",
            "email_notifications": True,
        }

        # Create a teammate for authentication (since users endpoints require auth)
        self.teammate_data = {
            "email": "teammate@example.com",
            "name": "Test Teammate",
            "password": "securepassword123",
        }
        self.teammate = Teammate.objects.create_user(**self.teammate_data)

        # Generate JWT token for authentication
        refresh = RefreshToken.for_user(self.teammate)
        self.access_token = str(refresh.access_token)

        # Set authentication header for all requests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_create_user_success(self):
        """Test successful user creation"""
        response = self.client.post(self.users_url, self.valid_user_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert user was created in database
        self.assertTrue(
            User.objects.filter(email=self.valid_user_data["email"]).exists()
        )

    def test_list_users_success(self):
        """Test listing users"""
        # Create test user
        User.objects.create(**self.valid_user_data)

        response = self.client.get(self.users_url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_user_duplicate_email(self):
        """Test creating user with duplicate email fails"""
        # Create user first
        User.objects.create(**self.valid_user_data)

        # Try to create another user with same email
        response = self.client.post(self.users_url, self.valid_user_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_get_user_detail(self):
        """Test retrieving user details"""
        user = User.objects.create(**self.valid_user_data)
        detail_url = f"{self.users_url}{user.id}/"

        response = self.client.get(detail_url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], user.email)
        self.assertEqual(response.data["full_name"], user.get_full_name())

    def test_update_user_success(self):
        """Test updating user data"""
        user = User.objects.create(**self.valid_user_data)
        detail_url = f"{self.users_url}{user.id}/"

        update_data = {"first_name": "Updated", "last_name": "Name"}

        response = self.client.patch(detail_url, update_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Refresh from database
        user.refresh_from_db()
        self.assertEqual(user.first_name, "Updated")
        self.assertEqual(user.last_name, "Name")

    def test_soft_delete_user(self):
        """Test soft deleting user (deactivation)"""
        user = User.objects.create(**self.valid_user_data)
        detail_url = f"{self.users_url}{user.id}/"

        response = self.client.delete(detail_url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # User should still exist but be inactive
        user.refresh_from_db()
        self.assertEqual(user.status, User.INACTIVE)
        self.assertFalse(user.is_active)


class UserAuthenticationTestCase(APITestCase):
    """Test cases for User Authentication endpoints"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        print("\n" + "=" * 50)
        print("🧪 RUNNING TESTS FOR USER AUTHENTICATION")
        print("=" * 50)

    def setUp(self):
        """Set up test data before each test"""
        self.register_url = "/api/users/internal/register/"
        self.login_url = "/api/users/login/"
        self.profile_url = "/api/users/me/"
        self.password_url = "/api/users/me/password/"
        self.validate_token_url = "/api/users/validate-token/"

        self.user_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User",
            "phone": "+1234567890",
            "password": "securepass123",
            "password_confirm": "securepass123",
            "email_notifications": True,
        }

    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post(self.register_url, self.user_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert user was created in database with password
        user = User.objects.get(email=self.user_data["email"])
        self.assertTrue(user.has_usable_password())
        self.assertTrue(user.check_password("securepass123"))

    def test_user_registration_password_mismatch(self):
        """Test registration fails with password mismatch"""
        invalid_data = self.user_data.copy()
        invalid_data["password_confirm"] = "differentpass"

        response = self.client.post(self.register_url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Passwords do not match", str(response.data))

    def test_user_registration_duplicate_email(self):
        """Test registration fails with duplicate email"""
        # Create user first
        User.objects.create(
            email=self.user_data["email"], first_name="First", last_name="User"
        )

        response = self.client.post(self.register_url, self.user_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_user_login_success(self):
        """Test successful user login"""
        # Create user first
        user = User.objects.create(
            **{
                k: v
                for k, v in self.user_data.items()
                if k not in ["password", "password_confirm"]
            }
        )
        user.set_password("securepass123")
        user.save()

        login_data = {"email": self.user_data["email"], "password": "securepass123"}

        response = self.client.post(self.login_url, login_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

        # Assert user data in response
        self.assertEqual(response.data["user"]["email"], user.email)

    def test_user_login_invalid_credentials(self):
        """Test login fails with invalid credentials"""
        login_data = {"email": "nonexistent@example.com", "password": "wrongpass"}

        response = self.client.post(self.login_url, login_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Invalid email or password", str(response.data))

    def test_user_profile_access(self):
        """Test user can access their own profile"""
        # Create and authenticate user
        user = User.objects.create(
            **{
                k: v
                for k, v in self.user_data.items()
                if k not in ["password", "password_confirm"]
            }
        )
        user.set_password("securepass123")
        user.save()

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.get(self.profile_url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], user.email)
        self.assertEqual(response.data["full_name"], user.get_full_name())

    def test_user_password_update(self):
        """Test user can update their password"""
        # Create and authenticate user
        user = User.objects.create(
            **{
                k: v
                for k, v in self.user_data.items()
                if k not in ["password", "password_confirm"]
            }
        )
        user.set_password("oldpass123")
        user.save()

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        password_data = {
            "current_password": "oldpass123",
            "new_password": "newpass123",
            "new_password_confirm": "newpass123",
        }

        response = self.client.put(self.password_url, password_data)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("Password updated successfully", response.data["message"])

        # Verify password was changed
        user.refresh_from_db()
        self.assertTrue(user.check_password("newpass123"))
        self.assertFalse(user.check_password("oldpass123"))

    def test_token_validation_endpoint(self):
        """Test token validation for inter-service communication"""
        # Create and authenticate user
        user = User.objects.create(
            **{
                k: v
                for k, v in self.user_data.items()
                if k not in ["password", "password_confirm"]
            }
        )
        user.set_password("securepass123")
        user.save()

        # Generate JWT token
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Set authentication header
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        response = self.client.get(self.validate_token_url)

        # Assert response
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["valid"])
        self.assertEqual(response.data["user_type"], "client")
        self.assertEqual(response.data["user"]["email"], user.email)

    def test_authentication_required_endpoints(self):
        """Test that protected endpoints require authentication"""
        # Test profile endpoint without auth
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test password update without auth
        response = self.client.put(self.password_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test token validation without auth
        response = self.client.get(self.validate_token_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
