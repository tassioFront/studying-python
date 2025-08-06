from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom serializer for obtaining JWT tokens with additional user claims.

    This serializer extends the default TokenObtainPairSerializer to include
    custom claims in the JWT token:
        - type: The user's type (e.g., role or user category).
        - is_active: Boolean indicating if the user account is active.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token["type"] = user.type
        token["is_active"] = user.is_active
        return token
