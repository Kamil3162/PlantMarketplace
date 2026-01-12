import json

import asyncio
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.apps import apps
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.http import HttpRequest
from asgiref.sync import sync_to_async

from data.models import CustomUser
from django.views.decorators.csrf import csrf_exempt
from forms import UserModify, RegisterForm, UserResetPassword
from utils import (
    get_user,
    get_user_by_email,
    generate_reset_email,
    generate_register_email,
    validate_page_number,
    send_email_async,
    get_objects_range
)
from exceptions import (
    UserPermissionDenied,
    UserNotFound,
    UserDataFormat,
    PageNumberException
)
from microservices_provider import EmailClient, SericeURLS
from .responses import ApiResponse
from microservices_provider import AuthClient, EmailClient

PAGE_SIZE = 15
AuthCLIENT = AuthClient()
EMAILCLIENT = EmailClient()


def users_list(request: HttpRequest):
    try:
        page = request.GET.get('page', default=1)

        page_number = validate_page_number(page)
        start, end = get_objects_range(page_number, PAGE_SIZE)

        users = CustomUser.objects.all()
        users = serializers.serialize('json', users, indent=2)

        return JsonResponse(
            data={
                'users': users,
                'page_number': page_number,
            }
        )
    except PageNumberException as e:
        return ApiResponse(
            type='error',
            detail=str(e),
            status_code=400
        )

@csrf_exempt
def user_modify(request: HttpRequest, user_data=None):
    if request.method == 'POST':

        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        user_email = data.get('email')
        user_obj = get_user_by_email(user_email)

        form = UserModify(request.POST, instance=user_obj)
        try:
            if form.is_valid():
                user = form.save()

                return JsonResponse({
                    'status': 'success',
                    'user_data': user_dict,
                    'message': 'User updated successfully'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Form validation failed',
                    'errors': form.errors
                })
        except ValidationError as exc:
            return JsonResponse({
                'status': exc.code,
                'message': str(exc.message)
            }, status=400)

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Unexpected error: {str(e)}'
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })


@csrf_exempt
def user_detail(request: HttpRequest):
    if request.method == 'GET':
        user_id = request.GET.get('user_id')
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'User not found'
                }, status=404)
        elif request.user.is_authenticated:
            user = request.user
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'User ID required or authentication needed'
            }, status=401)

        user_data = model_to_dict(user, fields=[
            'id',
            'first_name',
            'last_name',
            'email',
            'is_active',
            'is_confirmed',
            'is_staff',
            'created_at',
            'updated_at'
        ])

        if 'created_at' in user_data and user_data['created_at']:
            user_data['created_at'] = user_data['created_at'].isoformat()
        if 'updated_at' in user_data and user_data['updated_at']:
            user_data['updated_at'] = user_data['updated_at'].isoformat()

        return ApiResponse(
            type='success',
            detail=user_data,
            status_code=201
        )

    return ApiResponse(
        type='error',
        detail='Only GET method allowed',
        status_code=405
    )


@csrf_exempt
def reset_password(request: HttpRequest):
    if request.method == 'POST':
        email = request.POST.get('email')

        if not email:
            return JsonResponse({
                'status': 'error',
                'message': 'Email is required'
            })

        try:
            user = get_user_by_email(email)
            email_data = generate_reset_email(email, user)

            try:
                asyncio.run(send_email_async(email_data))
                return JsonResponse({
                    'status': 'success',
                    'message': 'Password reset email sent successfully'
                }, 201)
            except Exception as e:
                print(f"Failed to send reset email: {e}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to send reset email'
                }, status=500)

        except CustomUser.DoesNotExist:
            return JsonResponse({
                'status': 'success',
                'message': 'If this email exists, a reset link has been sent'
            }, status=401)

    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method allowed'
    }, status=405)


@csrf_exempt
def register(request: HttpRequest):
    """
    Function responsible for registering a new user
    """
    if request.method == 'POST':
        data = request.POST
        form = RegisterForm(data)
        try:
            if form.is_valid():
                user = form.save()
                user.is_confirmed = False
                user.save()

                user_dict = model_to_dict(user, fields=[
                    'id',
                    'first_name',
                    'last_name',
                    'email',
                    'is_active',
                    'is_confirmed'
                ])

                if 'created_at' in user_dict and user_dict['created_at']:
                    user_dict['created_at'] = user_dict[
                        'created_at'].isoformat()

                user_email = user.email
                email_data = generate_register_email(user_email, user)

                try:
                    email_result = asyncio.run(send_email_async(email_data))
                    email_sent = True
                except Exception as e:
                    print(f"Failed to send welcome email: {e}")
                    email_sent = False

                return JsonResponse({
                    'status': 'success',
                    'message': 'User registered successfully. Please check your email to activate your account.',
                })
        except ValidationError as e:
            return JsonResponse(
                {
                    'status': 'error',
                    'message': str(e)
                },
                status=400
            )
        return JsonResponse({
            'status': 'error',
            'message': f'Form validation failed {form.errors}'
        }, status=400)
    else:
        return JsonResponse({
            'status': 'error',
            'message': 'Only POST method allowed'
        }, status=405)


@csrf_exempt
def user_delete(request: HttpRequest, user_id:int):
    if request.method == 'DELETE':
        try:
            user = CustomUser.objects.get(id=user_id)
            user_email = user.email

            email_data = generate_del_email(user_email, user)

            asyncio.run(send_email_async(email_data))

            user.delete()

            return ApiResponse(
                type='success',
                detail='User deleted succesfully',
                status_code=401
            )

        except CustomUser.DoesNotExist:
            return ApiResponse(
                type='error',
                detail='User not found',
                status_code=404
            )

        except Exception as e:
            return ApiResponse(
                type='error',
                detail=str(e),
                status_code=500
            )

    return ApiResponse(
        type='error',
        detail='Only DELETE method allowed',
        status_code=405
    )


@csrf_exempt
def user_by_email(request: HttpRequest):
    try:
        if request.content_type == "application/json" and request.method == "POST":
            user_data = json.loads(request.body)
        elif request.method == "POST":
            user_data = request.POST

        user_email = user_data['email']
        user_password = user_data['password']

        user_object = authenticate(request, email=user_email, password=user_password)

        if not user_object:
            raise UserPermissionDenied("Your email or password is incorrect", 401)

        response = user_object.to_json()

        return ApiResponse(detail=response, status_code=200, type="success")
    except UserPermissionDenied as e:
        return ApiResponse(
            detail=e.detail,
            status_code=e.status_code,
            type="error"
        )


@csrf_exempt
async def reset_link(request: HttpRequest):
    if request.method != 'POST':
        return ApiResponse(
            type='error',
            detail='Only POST allowed',
            status_code=405
        )

    user_email = request.POST.get('email')

    if not user_email:
        return ApiResponse(
            type='error',
            detail='Email required',
            status_code=400
        )

    try:
        user = await sync_to_async(CustomUser.objects.get)(email=user_email)
        response = await AuthCLIENT.make_request(
            "/authenticate/reset/",
            method="POST",
            json_data={"user_id": user.id}
        )

        token = response["token"]

        await EMAILCLIENT.make_request("email/reset/", method="POST", json_data={
            "receiver": user.email,
            "subject": "Reset hasła",
            "body_text": f"http://localhost:8001/users/reset/password/?token={token}",
        })

        return ApiResponse(
            type='success',
            detail='Reset link has been sent',
            status_code=201
        )

    except CustomUser.DoesNotExist:
        return ApiResponse(
            type='error',
            detail='User not found',
            status_code=404
        )

    except Exception as e:
        return ApiResponse(
            type='error',
            detail=str(e),
            status_code=500
        )


@csrf_exempt
async def reset_url(request: HttpRequest):
    if request.method == "GET":
        token = request.GET.get('token')
        if not token:
            return ApiResponse(
                type='error',
                detail='Token required',
                status=401
            )

        return render(request, "reset_template.html", {
            'reset_form': UserResetPassword(),
            'token': token
        })

    if request.method == "POST":
        token = request.POST.get("token")
        new_password = request.POST.get("password")

        if not token or not new_password:
            return ApiResponse(
                {'error': 'Token and password required'},
                status=400
            )

        validation_response = await AuthCLIENT.make_request(
            "/authenticate/validate/",
            method="POST",
            json_data={"token": token}
        )

        if validation_response.get('valid'):
            user_id = validation_response.get('user_id')
            user = await sync_to_async(CustomUser.objects.get)(id=user_id)

            user.set_password(new_password)
            user.save()

            return ApiResponse(
                type='success',
                detail='User data modified',
                status_code=201
            )
        else:
            return ApiResponse(
                type='success',
                detail='Invalid token',
                status_code=400
            )

    return ApiResponse(
        type='error',
        detail='Method not allowed',
        status_code=405
    )


def consul_health(request: HttpRequest):
    print(request)
    return ApiResponse(
        detail='healthy',
        status_code=200,
        type='healthy',
    )

from django.shortcuts import render


def temp_url(request: HttpRequest):
    from forms import CustomUserForm

    users_queryset = CustomUser.objects.all()

    print(users_queryset)

    if request.method == "GET":
        print(dict(request))
        print(request.accepted_types)
        form = CustomUserForm()
        return render(request, "temp_template.html", {"form": form})

    else:
        form = CustomUserForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)
            print(form.fields)
            print(form.base_fields)
            print(form.inform())
            form.get_context()
            print("wszuystko jest gitr")
            form.save()
            users_queryset = CustomUser.objects.all()

            print(users_queryset)

            return JsonResponse(
                data={"esa": "ewasa"},
            )
