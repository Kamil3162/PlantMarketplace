import enum
from typing import Optional, Any

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin, UserManager, Group, Permission, ContentType

from phonenumber_field.modelfields import PhoneNumberField, PhoneNumber

class Address(models.Model):
    """
        Model reponsible for input detail delivery address for bought flowers
        etc.
    """
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    postal_code = models.CharField(max_length=10)
    city = models.CharField(max_length=20)
    street = models.CharField(max_length=50)
    apartment_number = models.CharField(max_length=10, blank=True)
    house_number = models.CharField(max_length=6, blank=True)
    mobile_phone = PhoneNumberField(blank=True)

    def __str__(self):
        return (f'Address '
                f'{self.first_name}'
                f'{self.last_name} '
                f'{self.postal_code} '
                f'{self.city}'
                f'{self.street}'
                f'{self.apartment_number}'
        )

    class Meta:
        app_label = 'data'
        verbose_name = 'Address'
        verbose_name_plural = 'Addresses'



class UserManager(BaseUserManager["CustomUser1"]):
    def create_user(
        self,
            #username,
            first_name, last_name, email,
        password=None, is_staff=False, is_active=True, **extra_fields
    ):
        """Create a user instance with the given email and password."""
        if first_name is None:
            raise ValueError('User first_name cannot be empty')

        if last_name is None:
            raise ValueError('User last_name cannot be empty')

        if email is None:
            raise ValueError('User email cannot be empty')

        email = self.normalize_email(email)
        # Google OAuth2 backend send unnecessary username field
        extra_fields.pop("username", None)

        user = self.model(
            first_name=first_name,last_name=last_name,email=email,
            is_active=is_active, is_staff=is_staff, **extra_fields
        )

        if password:
            user.set_password(password)
        user.save()
        return user

    def create_superuser(
        self,
        #username,
        email: str,
        first_name: str,
        last_name: str,
        password: Optional[str] = None,
        **extra_fields: Any
    ):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not extra_fields.get('is_staff'):
            raise ValueError('Superuser must have is_staff=True.')
        if not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            **extra_fields
        )

    def __call__(self, *args, **kwargs):
        print("test message")

class CustomUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=31)
    last_name = models.CharField(max_length=31)
    email = models.EmailField(null=False, unique=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']  # Required for createsuperuser
    objects = UserManager()

    class Meta:
        app_label = 'data'
        ordering = ('email',)

    def __str__(self):
        return f'CustomUser email={self.email}'




