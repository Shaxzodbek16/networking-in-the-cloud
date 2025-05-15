from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Creates default admin if not exists"

    def handle(self, *args, **kwargs):
        User = get_user_model()
        username = os.getenv("DEFAULT_ADMIN_USERNAME", "admin")
        password = os.getenv("DEFAULT_ADMIN_PASSWORD", "123")
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username, password=password, role="admin"
            )
            self.stdout.write(
                self.style.SUCCESS(f"Default admin '{username}' created.")
            )
        else:
            self.stdout.write(self.style.WARNING("Default admin already exists."))
