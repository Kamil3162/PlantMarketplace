from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator
from core.utils import check_access_token, admin_access_required

from .models import CustomUser, PermissionGroupAssigment
from .forms import UserModify
from .utils import get_user

# @admin_access_required
def users_list(request):
    # test group s and permissions for user
    users = CustomUser.objects.all()
    paginator = Paginator(users, 15)
    page = request.GET.get('page', default=1)

    print(paginator.num_pages)
    print(paginator.count)
    print(paginator.page_range)
    print(paginator.get_page(1))
    page_objects = paginator.get_page(1)
    print(page_objects.object_list)

    # print(PermissionGroupAssigment.objects.create_object())
    # print(PermissionGroupAssigment.objects.all())
    # print(user.get_user_permissions())
    # print(Permission.objects.all())
    # print(ContentType.objects.all())
    # print(Group.objects.all())
    # print(PermissionGroupAssigment.objects.filter(user=user)[0].group.permissions)

    users = CustomUser.objects.all()

    users = serializers.serialize('json', users, indent=2)
    return HttpResponse(users, content_type="application/json")

@check_access_token(required_group=None)
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

@check_access_token(required_group='account_modify')
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








