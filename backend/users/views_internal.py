from urllib.parse import unquote
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import generics, permissions, status

from rest_framework import status
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)

from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from .models import User
from .serializers import (UserSerializer, UserRegistrationSerializer)


@api_view(["GET"])
@authentication_classes([])
@permission_classes([])
def get_user_by_email(request, email):
    """
    Get user details by email
    GET /api/users/by-email/<email>/
    """
    decoded_email = unquote(email)
    try:
        validate_email(decoded_email)
    except ValidationError:
        return Response(
            {"detail": "Invalid email format."}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        user = User.objects.get(email=decoded_email)
    except User.DoesNotExist:
        raise NotFound("User not found.")
    return Response(UserSerializer(user).data, status=status.HTTP_200_OK)


# User Authentication Views
class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint - allows users to self-register
    POST /api/users/register/ - Register new user with password
    """

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        serializer.save(date_joined=timezone.now())
