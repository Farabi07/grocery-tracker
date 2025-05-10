from django.db import models

from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('employee', 'Employee'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')

    def __str__(self):
        return self.username
