import json

import asyncio
from django.http import JsonResponse, HttpResponse
from django.core import serializers
from django.shortcuts import render
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.apps import apps
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth import authenticate, login
from django.http import HttpRequest


from data.models import CustomUser
from forms import UserModify, RegisterForm  # Dodaj RegisterForm import
from utils import get_user, get_user_by_email
from exceptions import UserPermissionDenied, UserNotFound, UserDataFormat
from microservices_provider import EmailClient, SericeURLS
from .responses import CustomResponse


PAGE_SIZE = 15

async def send_email_async(email_data, method):
    """Helper function to send emails asynchronously"""
    try:
        email_service = EmailClient()
        endpoint = "/email/send/"  # Dostosuj endpoint
        response = await email_service.make_request(
            endpoint,
            method=method,
            data=email_data
        )
        return response
    except Exception as e:
        print(f"Email sending error: {e}")
        return None


def users_list(request):
    page = request.GET.get('page', default=1)
    start = (int(page) - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    users = CustomUser.objects.all()[start:end]
    users = serializers.serialize('json', users, indent=2)

    endpoint = "/email/base/"
    email_service = EmailClient()
    try:
        email_response = asyncio.run(
            email_service.make_request(endpoint, method='GET')
        )
    except Exception as e:
        print(f"Email service error: {e}")
        email_response = None

    return HttpResponse(users, content_type="application/json")


@csrf_exempt
def user_modify(request, user_data=None):
    if request.method == 'POST':

        if request.content_type == 'application/json':
            import json
            data = json.loads(request.body)
            user_email = data.get('email')
        else:
            # Standardowe form data
            user_email = request.POST.get('email')
            data = request.POST

        user_email = user_email
        user_obj = get_user_by_email(user_email)

        old_user_data = {
            'email': user_obj.email,
            'first_name': user_obj.first_name,
            'last_name': user_obj.last_name,
            'is_active': user_obj.is_active,
            'is_confirmed': user_obj.is_confirmed,
        }

        form = UserModify(request.POST, instance=user_obj)
        try:
            if form.is_valid(raise_exception=True):
                user = form.save()
                user_dict = model_to_dict(user, fields=[
                    'email',
                    'first_name',
                    'last_name',
                    'is_active',
                    'is_confirmed',
                ])

                email_data = {
                    'to_email': user.email,
                    'subject': 'Your Account Has Been Updated',
                    'template': 'user_modified',
                    'context': {
                        'user_name': user.first_name,
                        'user_last_name': user.last_name,
                        'old_data': old_user_data,
                        'new_data': user_dict,
                        'modified_fields': [
                            field for field in
                            ['email', 'first_name', 'last_name', 'is_active']
                            if old_user_data.get(field) != user_dict.get(field)
                        ],
                        'update_time': timezone.now().strftime(
                            '%Y-%m-%d %H:%M:%S')
                    }
                }

                try:
                    asyncio.run(send_email_async(email_data, "POST"))
                    print(f"Modification email sent to {user.email}")
                except Exception as e:
                    print(f"Failed to send modification email: {e}")

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
def user_detail(request):
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

        return JsonResponse({
            'status': 'success',
            'user_data': user_data
        })

    return JsonResponse({
        'status': 'error',
        'message': 'Only GET method allowed'
    }, status=405)


@csrf_exempt
def reset_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if not email:
            return JsonResponse({
                'status': 'error',
                'message': 'Email is required'
            })

        try:
            user = get_user_by_email(email)

            email_data = {
                'to_email': email,
                'subject': 'Password Reset Request - PlantMarketplace',
                'template': 'password_reset',
                'context': {
                    'user_name': user.first_name,
                    'user_last_name': user.last_name,
                    'user_id': user.id,
                    'reset_link': f"http://yourdomain.com/reset-password/{user.id}/",
                    'platform_name': 'PlantMarketplace',
                    'request_time': timezone.now().strftime(
                        '%Y-%m-%d %H:%M:%S'),
                    'support_email': 'support@plantmarketplace.com'
                }
            }

            try:
                asyncio.run(send_email_async(email_data))
                return JsonResponse({
                    'status': 'success',
                    'message': 'Password reset email sent successfully'
                })
            except Exception as e:
                print(f"Failed to send reset email: {e}")
                return JsonResponse({
                    'status': 'error',
                    'message': 'Failed to send reset email'
                })

        except CustomUser.DoesNotExist:
            # Ze względów bezpieczeństwa nie ujawniamy czy email istnieje
            return JsonResponse({
                'status': 'success',
                'message': 'If this email exists, a reset link has been sent'
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Only POST method allowed'
    }, status=405)


@csrf_exempt
def register(request):
    """
    Function responsible for registering a new user
    """
    if request.method == 'POST':
        data = request.POST
        form = RegisterForm(data)
        try:
            if form.is_valid():
                user = form.save()
                # Ustaw is_confirmed na False - user musi potwierdzić email
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

                email_data = {
                    'to_email': user.email,
                    'subject': 'Welcome to PlantMarketplace - Please Confirm Your Account',
                    'template': 'welcome_registration',
                    'context': {
                        'user_name': user.first_name,
                        'user_last_name': user.last_name,
                        'user_email': user.email,
                        'user_id': user.id,
                        'activation_link': f"http://yourdomain.com/activate/{user.id}/",
                        'platform_name': 'PlantMarketplace',
                        'registration_date': user.created_at.strftime(
                            '%Y-%m-%d %H:%M:%S'),
                        'support_email': 'support@plantmarketplace.com'
                        # Dostosuj
                    }
                }

                # Wyślij email asynchronicznie
                try:
                    email_result = asyncio.run(send_email_async(email_data))
                    print(
                        f"Welcome email sent to {user.email}: {email_result}")
                    email_sent = True
                except Exception as e:
                    print(f"Failed to send welcome email: {e}")
                    email_sent = False

                return JsonResponse({
                    'status': 'success',
                    'user_data': user_dict,
                    'message': 'User registered successfully. Please check your email to activate your account.',
                    'email_sent': email_sent
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
def user_delete(request, user_id):
    if request.method == 'DELETE':
        try:
            user = CustomUser.objects.get(id=user_id)

            # Wyślij email o usunięciu konta
            email_data = {
                'to_email': user.email,
                'subject': 'Account Deletion Confirmation',
                'template': 'account_deleted',
                'context': {
                    'user_name': user.first_name,
                    'user_last_name': user.last_name,
                    'deletion_date': timezone.now().strftime(
                        '%Y-%m-%d %H:%M:%S'),
                    'registration_date': user.created_at.strftime('%Y-%m-%d'),
                    'platform_name': 'PlantMarketplace',
                    'support_email': 'support@plantmarketplace.com'
                }
            }

            # Wyślij email przed usunięciem
            try:
                asyncio.run(send_email_async(email_data))
                print(f"Deletion notification sent to {user.email}")
            except Exception as e:
                print(f"Failed to send deletion email: {e}")

            user.delete()
            return JsonResponse({
                'status': 'success',
                'message': 'User deleted successfully'
            })
        except CustomUser.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'User not found'
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Only DELETE method allowed'
    }, status=405)

@csrf_exempt
def user_by_email(request):
    try:
        if request.content_type == "application/json" and request.method == "POST":
            print('application json')
            user_data = json.loads(request.body)
        elif request.method == "POST":
            user_data = request.POST
            print('post form data')

        print(user_data)

        user_email = user_data['email']
        user_password = user_data['password']

        user_object = authenticate(request, email=user_email, password=user_password)

        if not user_object:
            raise UserPermissionDenied("Your email or password is incorrect", 403)
        else:
            response = user_object.to_json()

        return CustomResponse(detail=response, status_code=200, type="success")
    except UserPermissionDenied as e:
        return CustomResponse(
            detail=e.detail,
            status_code=e.status_code,
            type="error"
        )

@csrf_exempt
def reset_link(request):

    print(request)

    if request.method == 'GET':
        raise MethodException('Following endpoint doesnt handle get method')

    user_email = request.POST.get('email')

    if not user_email:
        raise UserDataFormat('Following user doesnt exists')

    # we have to make orm
    user = CustomUser.objects.filter(email=user_email)

    if not user:
        raise UserNotFound('User with following email doesnt exists')

    # if yes
    # we have to generate temp token to reset our password
    return JsonResponse(
        data={
            'status': 'esa'
        }
    )

