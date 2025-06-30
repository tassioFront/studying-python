from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("type", User.SUPERUSER)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ADMIN = "admin"
    SUPERUSER = "superuser"
    DEVELOPER = "developer"

    TYPE_CHOICES = [
        (ADMIN, "Admin"),
        (SUPERUSER, "Superuser"),
        (DEVELOPER, "Developer"),
    ]

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=DEVELOPER)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    @property
    def is_staff(self):
        """Admin and superuser teammates have staff access"""
        return self.type in [self.ADMIN, self.SUPERUSER]

    def __str__(self):
        """String representation of user returns their email"""
        return self.email
