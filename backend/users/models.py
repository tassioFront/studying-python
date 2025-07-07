import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.db import models
from django.utils import timezone


class User(models.Model):
    """
    Client User model - for external users/customers
    This is separate from teammates (internal team members)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"

    STATUS_CHOICES = [
        (ACTIVE, "Active"),
        (INACTIVE, "Inactive"),
        (SUSPENDED, "Suspended"),
    ]

    # Basic information
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True, null=True)

    password = models.CharField(
        max_length=128,
        blank=True,
        null=True,
        help_text="Password for user authentication (optional for now)",
    )

    # Status and dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=ACTIVE)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(blank=True, null=True)

    # Preferences
    email_notifications = models.BooleanField(default=True)

    class Meta:
        db_table = "users_user"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

    @property
    def is_active(self):
        return self.status == self.ACTIVE

    def set_password(self, raw_password):
        if raw_password:
            self.password = make_password(raw_password)
        else:
            self.password = None

    def check_password(self, raw_password):
        if not self.password:
            return False
        return check_password(raw_password, self.password)

    def has_usable_password(self):
        return bool(self.password)

    @property
    def is_authenticated(self):
        """Always return True for authenticated users"""
        return True

    @property
    def is_anonymous(self):
        """Always return False for authenticated users"""
        return False

    @property
    def pk(self):
        """Return primary key for JWT token generation"""
        return self.id

    def get_username(self):
        """Return email as username for JWT compatibility"""
        return self.email
