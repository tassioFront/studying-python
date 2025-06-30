from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken
from django.contrib.auth import get_user_model
from users.models import User as ClientUser


class MultiUserJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that supports both teammate and client user models
    """
    
    def get_user(self, validated_token):
        try:
            user_id = validated_token['user_id']
        except KeyError:
            raise InvalidToken('Token contained no recognizable user identification')

        TeammateUser = get_user_model()
        try:
            user = TeammateUser.objects.get(pk=user_id)
            if user.is_active:
                return user
        except TeammateUser.DoesNotExist:
            pass

        try:
            user = ClientUser.objects.get(pk=user_id)
            if user.is_active:
                return user
        except ClientUser.DoesNotExist:
            pass

        raise InvalidToken('User not found')
