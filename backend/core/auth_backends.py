from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from teammates.models import User as Teammate
from users.models import User as ClientUser


class MultiUserBackend(BaseBackend):
    """
    Custom authentication backend that supports both teammates and client users
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None or password is None:
            return None

        try:
            teammate = Teammate.objects.get(email=username)
            if teammate.check_password(password):
                return teammate
        except Teammate.DoesNotExist:
            pass

        try:
            user = ClientUser.objects.get(email=username, status=ClientUser.ACTIVE)
            if user.check_password(password):
                return user
        except ClientUser.DoesNotExist:
            pass

        return None

    def get_user(self, user_id):
        Teammate = get_user_model()
        try:
            return Teammate.objects.get(pk=user_id)
        except Teammate.DoesNotExist:
            pass

        try:
            return ClientUser.objects.get(pk=user_id)
        except ClientUser.DoesNotExist:
            pass

        return None
