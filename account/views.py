from django.http import JsonResponse
from django.core import serializers

from .models import CustomUser

def users_list(request):
    print(request.method)
    users = serializers.serialize('json', CustomUser.objects.all())
    return JsonResponse({'users':users})

def user_modify(request):
    pass

def user_detail(request):
    # get user detail and display this
    pass




