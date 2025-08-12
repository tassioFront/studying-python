from django.utils import timezone

from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from users.jwt_serializers import CustomTokenObtainPairSerializer

from .models import User
from .serializers import (
    UserAuthSerializer,
    UserCreateSerializer,
    UserInitialPasswordSerializer,
    UserPasswordUpdateSerializer,
    UserRegistrationSerializer,
    UserSerializer,
    UserTokenValidationSerializer,
    UserUpdateSerializer,
)


class UserListCreateView(generics.ListCreateAPIView):
    """
    List all users or create a new user
    Requires authentication - only teammates can access
    """

    queryset = User.objects.filter(status=User.ACTIVE)
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UserCreateSerializer
        return UserSerializer

    def perform_create(self, serializer):
        serializer.save(date_joined=timezone.now())


class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a user
    Requires authentication - only teammates can access
    GET /api/users/{id}/ - Get user details
    PUT /api/users/{id}/ - Update user
    PATCH /api/users/{id}/ - Partial update user
    DELETE /api/users/{id}/ - Delete user (sets status to inactive)
    """

    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserSerializer

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.status = User.INACTIVE
        user.save()
        return Response(
            {"message": "User deactivated successfully"}, status=status.HTTP_200_OK
        )


# User Authentication Views
class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint - allows users to self-register
    POST /api/users/register/ - Register new user with password
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save(date_joined=timezone.now())


class UserLoginView(generics.GenericAPIView):
    """
    User login endpoint - returns JWT tokens for authenticated users
    POST /api/users/login/ - Login user and return JWT tokens
    """

    serializer_class = UserAuthSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        user.last_login = timezone.now()
        user.save()

        # Generate JWT tokens with custom claims
        refresh = CustomTokenObtainPairSerializer.get_token(user)

        return Response(
            {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile endpoint - allows users to view/update their own profile
    GET /api/users/me/ - Get current user profile
    PUT/PATCH /api/users/me/ - Update current user profile
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Ensure the user is a User instance (not Teammate)
        # Check if it's a client user by checking the model class name
        if (
            hasattr(self.request.user, "_meta")
            and self.request.user._meta.app_label == "users"
        ):
            return self.request.user
        else:
            # If authenticated as teammate, raise error
            from rest_framework.exceptions import NotFound

            raise NotFound("User not found")

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return UserUpdateSerializer
        return UserSerializer


class UserPasswordUpdateView(generics.UpdateAPIView):
    """
    User password update endpoint
    PUT /api/users/me/password/ - Update user password
    """

    serializer_class = UserPasswordUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        if (
            hasattr(self.request.user, "_meta")
            and self.request.user._meta.app_label == "users"
        ):
            return self.request.user
        else:
            from rest_framework.exceptions import NotFound

            raise NotFound("User not found")

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user.set_password(serializer.validated_data["new_password"])
        user.save()

        return Response(
            {"message": "Password updated successfully"}, status=status.HTTP_200_OK
        )


class UserSetInitialPasswordView(generics.GenericAPIView):
    """
    Initial password setting endpoint - for users created without password
    POST /api/users/set-password/ - Set initial password for user
    """

    serializer_class = UserInitialPasswordSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        password = serializer.validated_data["password"]

        user.set_password(password)
        user.save()

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "message": "Password set successfully",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "user": UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
@permission_classes([permissions.IsAuthenticated])
def validate_user_token(request):
    """
    Token validation endpoint for inter-service communication
    GET /api/users/validate-token/ - Validate JWT token and return user info
    Used by projects-service to validate user tokens
    """
    user = request.user

    # Check if it's a User (client) or Teammate
    if isinstance(user, User):
        serializer = UserTokenValidationSerializer(
            {
                "user_id": user.id,
                "email": user.email,
                "full_name": user.get_full_name(),
                "status": user.status,
                "is_active": user.is_active,
                "type": user.type,
            }
        )
        return Response(
            {"valid": True, "user_type": "client", "user": serializer.data},
            status=status.HTTP_200_OK,
        )
    else:
        # It's a teammate
        return Response(
            {
                "valid": True,
                "user_type": "teammate",
                "user": {
                    "user_id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "type": user.type,
                    "is_active": True,
                },
            },
            status=status.HTTP_200_OK,
        )


@api_view(["GET"])
def get_user_by_email(request, email):
    """
    Get user details by email
    GET /api/users/by-email/<email>/
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise NotFound("User not found.")
    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)
