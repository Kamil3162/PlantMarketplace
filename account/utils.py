from .models import CustomUser


def get_user(email):
    return CustomUser.objects.get(email=email)