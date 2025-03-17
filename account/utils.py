from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser

def get_user(user_id: int):
    """
        Retrieve a user by email with custom error message.
    """
    return CustomUser.objects.get(id=user_id)







