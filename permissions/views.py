from django.shortcuts import render
from django.http import HttpResponse

from .models import PermissionGroupAssigment
# Create your views here.

def get_permissions(request):
    # in this line on code i wanna generate permission following my scheme
    permission = PermissionGroupAssigment.objects._create_permissions()
    groups = PermissionGroupAssigment.objects._generate_base_groups()
    return HttpResponse('success')
