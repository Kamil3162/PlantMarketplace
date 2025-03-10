import enum
from typing import Optional, Any

from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, \
    PermissionsMixin, UserManager, Group, Permission, ContentType

from phonenumber_field.modelfields import PhoneNumberField, PhoneNumber
from .exceptions import PermissionGroupError, PermissionGroupExists, \
    UserNotFound, PermissionGroupDenied


# # Create your models here.
# class Address(models.Model):
#     """
#         Model reponsible for input detail delivery address for bought flowers
#         etc.
#     """
#     first_name = models.CharField(max_length=30)
#     last_name = models.CharField(max_length=30)
#     postal_code = models.CharField(max_length=10)
#     city = models.CharField(max_length=20)
#     street = models.CharField(max_length=50)
#     apartment_number = models.CharField(max_length=10, blank=True)
#     house_number = models.CharField(max_length=6, blank=True)
#     mobile_phone = PhoneNumberField(blank=True)

class UserManager(BaseUserManager["CustomUser"]):
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
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
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
        app_label = 'account'
        ordering = ('email',)

    def __str__(self):
        return f'CustomUser email={self.email}'


class PermissionGroupManager(models.Manager):
    """
        Assign a user to a group with a specific permission role.
    """

    def assign_group(self, user, permission_role, group_name=None):
        permission_groups = self.model.GROUPS
        if permission_role not in [group[0] for group in permission_groups]:
            raise PermissionGroupError('Permission role does not exist')

        try:
            user_group_assigned = self.fetch_permission_group(user)
            if user_group_assigned.role_type == permission_role:
                raise PermissionGroupExists(
                    'User already has this permission role')
        except self.model.DoesNotExist:
            raise UserNotFound('User does not exist')

        # Create or get the group
        group, _ = Group.objects.get_or_create(
            name=group_name or permission_role)

        # Create assignment
        return self.model.objects.create(
            user=user,
            group=group,
            role_type=permission_role
        )

    def fetch_user_group_permissions(self, user):
        return self.model.objects.get(user=user)

    def create_permission_group(self, use_id=None):
        # get_or_create returns a tuple of (object, created), so we need to access the first element
        permission, _ = Permission.objects.get_or_create(
            codename='modify_account',
            # You need to supply content_type and name when creating a permission
            name='Can modify account',
            content_type=ContentType.objects.get_for_model(CustomUser)
            # Assuming this is for CustomUser model
        )

        # Same issue with get_or_create returning a tuple
        group, _ = Group.objects.get_or_create(name='account_modify')
        group.permissions.add(permission)

        # Consider making the user ID a parameter instead of hardcoding
        user = CustomUser.objects.get(id=2)
        user.groups.add(group)

        # The saves aren't necessary after add() operations as Django handles this automatically

        # Assuming the field is correctly named role_type in your model, not content_type
        perm_group_assignment = PermissionGroupAssigment.objects.create(
            group=group,
            user=user,
            role_type='CUSTOMER',
            # Using the correct field name from your model
        )

        return perm_group_assignment


    def change_permission_group(self, group_codename, user_id):
        try:
            user = CustomUser.objects.get(id=user_id)
            permission_group = self.model.objects.get(codename=group_codename)

            if not permission_group:
                raise PermissionGroupError('Permission group does not exist')

            user_group_assigned = self.fetch_permission_group()

            if group_codename is user_group_assigned.role_type:
                raise PermissionGroupExists('User already have a this permission group')

            user_group_assigned.role_type = group_codename
            user_group_assigned.save()
            return user_group_assigned
        except CustomUser.DoesNotExist:
            raise UserNotFound('User does not exist')
        except PermissionGroupExists:
            raise PermissionGroupError('Permission group already exists')
        except Exception as e:
            raise Exception(str(e))

    def check_permission_group(self, user, group_codename):
        try:
            permission_group = self.fetch_permission_group(user).role_type
            if not permission_group:
                raise PermissionGroupError('Permission group does not exist')

            target_permission_group = Group.objects.get(name=group_codename)

            if permission_group is not target_permission_group.name:
                raise PermissionGroupDenied('Permission denied')

            return True
        except PermissionGroupDenied:
            return False
        except PermissionGroupError as e:
            return False
        except Exception as e:
            raise Exception(str(e))


class PermissionGroupAssigment(models.Model):
    """
        Links users to permission groups with descriptive role names.
        This creates a three-way relationship between users, groups, and role types.
    """

    GROUPS = (
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Managers'),
        ('CUSTOMER', 'Customer'),
        ('ADMINISTRATOR', 'Administrator'),
        ('EDITOR', 'Content Editor'),
    )

    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=False)

    role_type = models.CharField(
        choices=GROUPS,
        default='CUSTOMER',
        max_length=25
    )

    objects = PermissionGroupManager()

    class Meta:
        verbose_name = "User Group Assignment"
        verbose_name_plural = "User Group Assignments"

    def __str__(self):
        return f"{self.user.get_username()} - {self.role_type}"