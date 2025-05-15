from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ("admin", "Admin"),
        ("manager", "Manager"),
        ("staff", "Staff"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="staff")

    class Meta:
        ordering = ["date_joined"]

    def get_role_display(self):
        return self.role

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
