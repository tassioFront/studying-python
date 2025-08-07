from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for obtaining JWT tokens with additional user claims.

    This serializer extends the default TokenObtainPairSerializer to include
    custom claims in the JWT token:
        - type: The user's type (e.g., role or user category).
        - status: The user's status (e.g., active, inactive, suspended).
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["type"] = getattr(user, "type", None)
        token["status"] = getattr(user, "status", User.INACTIVE)
        return token
