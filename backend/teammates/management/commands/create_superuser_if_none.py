from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from decouple import config


# it is a fake project hosted on Render
# This command creates a superuser teammate if one does not exist
class Command(BaseCommand):
    help = "Create a superuser teammate if one does not exist"

    def handle(self, *args, **options):
        User = get_user_model()

        # Get superuser credentials from environment variables
        email = config("SUPERUSER_EMAIL", default=None)
        name = config("SUPERUSER_NAME", default=None)
        password = config("SUPERUSER_PASSWORD", default=None)

        # Validate required fields
        if not email:
            self.stdout.write(self.style.ERROR("email is required"))
            return

        if not name:
            self.stdout.write(self.style.ERROR("name is required"))
            return

        if not password:
            self.stdout.write(self.style.ERROR("password is required"))
            return

        if not User.objects.filter(type=User.SUPERUSER).exists():
            User.objects.create_superuser(email=email, name=name, password=password)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Superuser teammate created successfully with email: {email}"
                )
            )
        else:
            superuser_emails = list(
                User.objects.filter(type=User.SUPERUSER).values_list("email", flat=True)
            )
            self.stdout.write(
                self.style.WARNING(
                    f"Superuser teammate already exists: {', '.join(superuser_emails)}"
                )
            )
