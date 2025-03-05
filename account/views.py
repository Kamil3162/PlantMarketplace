from django.http import JsonResponse, HttpResponse
from django.core import serializers

from .models import CustomUser
from core.utils import check_access_token

def users_list(request):
    print(request.method)
    users = serializers.serialize('json', CustomUser.objects.all())
    return JsonResponse({'users':users})

def user_modify(request):
    # TODO document why this method is empty
    pass

@check_access_token
def user_detail(request):
    pass




