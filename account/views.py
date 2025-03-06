from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from core.utils import check_access_token, admin_access_required

from .models import CustomUser
from .forms import UserModify
from .utils import get_user

@admin_access_required
def users_list(request):
    users = serializers.serialize('json', CustomUser.objects.all())
    return JsonResponse({'users':users})

@check_access_token
def user_modify(request, user_data=None):
    if request.method == 'POST':
        user_email = user_data['email']
        user_obj = get_user(user_email)
        form = UserModify(request.POST, instance=user_obj)
        try:
            if form.is_valid():
                user = form.save()
                user_dict = model_to_dict(user_obj, fields=[
                    'email',
                    'first_name',
                    'last_name',
                    'email'
                ])
                return JsonResponse({
                    'status': 'success',
                    'user_data': user_dict
                })
        except ValidationError as e:
            raise ValidationError(str(e))
        return HttpResponse('esa')

@check_access_token
def user_detail(request, user_data=None):
    user_form = UserModify()
    return render(
        request,
        'user_detail.html',
        {
            'user_form': user_form,
            'user_data': user_data
        },
    )

# url for admin data modify
def admin_user_modify(request):
    pass








