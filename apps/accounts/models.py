from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'Користувач'
        ADMIN = 'admin', 'Адміністратор'

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.USER,
    )

    def is_site_admin(self):
        return self.role == self.Role.ADMIN

    def __str__(self):
        return f'{self.username} ({self.get_role_display()})'
