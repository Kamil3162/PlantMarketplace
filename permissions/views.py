from django.http import HttpResponse
from core.utils import check_access_token

# Create your views here.

def get_permissions(request):

    return HttpResponse('success')

@check_access_token
def change_user_permission(request):
    pass
