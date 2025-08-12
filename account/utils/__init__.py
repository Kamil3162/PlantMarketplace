from functools import wraps

from django.core.exceptions import ObjectDoesNotExist
from data.models import CustomUser

from .email_data import (
    generate_del_email,
    generate_reset_email,
    generate_register_email,
    send_email_async
)
from .page import get_objects_range
from .validation import validate_page_number

def get_user(user_id: int):
    """
        Retrieve a user by email with custom error message.
    """
    try:
        return CustomUser.objects.get(id=user_id)
    except ObjectDoesNotExist as e:
        raise ObjectDoesNotExist(f"Object with id {user_id} does not exist. {str(e)}")


def get_user_by_email(email: str):
    try:
        return CustomUser.objects.get(email=email)
    except ObjectDoesNotExist as e:
        raise ObjectDoesNotExist(f"Object with email {email} does not exist. {str(e)}")


__all__ = [
    "get_user",
    "get_user_by_email",
    "generate_email_content",
    "generate_del_email",
    "validate_page_number",
    "send_email_async",
    "get_objects_range"
]