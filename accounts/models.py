from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrator'
        EMPLOYEE = 'EMPLOYEE', 'Employee'

    email = models.EmailField(unique=True, verbose_name='Email Address')
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.EMPLOYEE,
        verbose_name='User Role',
        help_text='Designates whether the user is an Administrator or an Employee.'
    )
    contact_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Contact Number'
    )
    department = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Department / Office'
    )
    employee_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Employee / Staff ID'
    )
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
        verbose_name='Profile Photo'
    )

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    @property
    def is_employee_role(self):
        return self.role == self.Role.EMPLOYEE

    @property
    def display_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.username

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
