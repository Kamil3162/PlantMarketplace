from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from .models import CustomUser
def get_user(user_id: int):
    """
        Retrieve a user by email with custom error message.
    """
    try:
        return CustomUser.objects.get(id=user_id)
    except ObjectDoesNotExist as e:
        raise ObjectDoesNotExist(f"Object with id {user_id} does not exist. {str(e)}")







