from django.db import models
from django.contrib.auth.models import Group, Permission, ContentType

from account.models import CustomUser
from account.exceptions import UserNotFound
from .exceptions import (
    PermissionGroupError,
    PermissionGroupExists,
    PermissionGroupDenied,
    ModelDoesNotExists
)
from .roles import ROLE_PERMISSIONS
from .permisions import PERMISSIONS
from .utils import generate_permission_name, get_permission_codenames

class PermissionGroupManager(models.Manager):
    """
        Assign a user to a group with a specific permission role.
    """

    def assign_group(self, user, permission_role, group_name=None):
        permission_groups = self.model.GROUPS

        if permission_role not in [group[0] for group in permission_groups]:
            raise PermissionGroupError('Permission role does not exist')

        user_group_assigned = self.fetch_permission_group(user)

        if len(user_group_assigned):
            for permission_group in user_group_assigned:
                if permission_group.role_type == permission_role:
                    raise PermissionGroupExists(
                        'User already has this permission role'
                    )

        # Create or get the group
        group, _ = Group.objects.get_or_create(
            name=group_name or permission_role)

        # Create assignment
        return self.model.objects.create(
            user=user,
            group=group,
            role_type=permission_role
        )

    def fetch_permission_group(self, user):
        return self.model.objects.filter(user=user)

    def create_permission_group(self, user_id=None):
        """
            Function responsible for creating a new permission group and assigning
            user for specific new created permission group
        Args:
            user_id: int - user id
        Returns:
            PermissionGroupAssigment - new assigned permission group for user
        """
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
        perm_group_assignment = PermissionGroupAssigment.objects.get_or_create(
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

            user_group_assigned = self.fetch_permission_group(user)

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

    def _create_permissions(self):
        try:
            content_type = ContentType.objects.get_for_model(CustomUser)
            permissions = []
            for permission_group in PERMISSIONS:
                for permission in permission_group:

                    # Extract codename from EnumClass
                    permission_codename = permission.codename

                    # Extract permission value from EnumClass
                    permission_name = generate_permission_name(permission)

                    # Create or get permission model object
                    permission, _ = Permission.objects.get_or_create(
                        name=permission_name,
                        content_type=content_type,
                        codename=permission_codename
                    )
                    permissions.append(permission)
            return permissions

        except CustomUser.DoesNotExists:
            raise ModelDoesNotExists('CustomUser model does not exist')

        except Exception as e:
            # exception used only during development
            raise Exception(str(e))

    def _generate_base_groups(self):
        try:
            group_names = ROLE_PERMISSIONS.keys()
            group_list = []
            for group_name in group_names:
                role_permissions = get_permission_codenames(
                    ROLE_PERMISSIONS,
                    group_name
                )

                permissions = Permission.objects.filter(
                    codename__in=role_permissions
                ).prefetch_related('content_type')

                group, _ = Group.objects.get_or_create(name=group_name)

                for permission in permissions:
                    group.permissions.add(permission)

                # only for dev purpose
                print(
                    'Successfully generated base permissions for group',
                    group_name
                )
                group_list.append(group)

            return group_list
        except Exception as e:
            raise Exception(str(e))

    def check_group_permission(self, user, group_codename=None):
        try:
            return self.model.objects.check_permission_group(
                user, group_codename
            )
        except Exception as e:
            return False

class PermissionGroupAssigment(models.Model):
    """
        Links users to permission groups with descriptive role names.
        This creates a three-way relationship between users, groups, and role types.
    """

    GROUPS = (
        ('ADMIN', 'Administrator'),
        ('MANAGER', 'Managers'),
        ('CUSTOMER_SERVICE', 'Customer Service'),
        ('CONTENT_EDITOR', 'Content Editor'),
        ('CUSTOMER', 'Customer'),
        ('ANONYMOUS', 'Anonymous user'),
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





