from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser, PermissionGroupAssigment

def get_user(user_id):
    """
        Retrieve a user by email with custom error message.
    """
    return CustomUser.objects.get(id=user_id)


def check_group_permission(user, group_codename=None):
    try:
        return PermissionGroupAssigment.objects.check_permission_group(
        user, group_codename
    )
    except Exception as e:
        return False




