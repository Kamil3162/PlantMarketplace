import json
import asyncio

import jwt
from django.shortcuts import render
from django.core.serializers import base
from django.http import HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
from django.utils import timezone

from microservices_provider import UserClient
from data.models import BlackListedTokens
from mechanism.redis_manager import RedisManager
from broker_opps.manager import rabbit_producer
from mechanism import RedisManager, JWTManager
from data.models import RefreshToken, ResetPasswordToken
from core.exceptions import TokenDoesNotExistError
from utils.helpers import create_response_token, create_success_token_response

redis_manager = RedisManager()
user_client = UserClient()


@csrf_exempt
async def login(request: HttpRequest):
    try:
        path = "/user/email"

        if request.content_type == "application/json":
            data_json = json.loads(request.body.decode('utf-8'))
        else:
            data_json = request.POST

        response = await user_client.make_request(
            path,
            method=request.method,
            json_data=data_json
        )

        user_data = response['detail']
        user_id = user_data['id']

        access_token, user_payload = JWTManager.create_access_token(user_id)
        refresh_token = JWTManager.create_refresh_token(user_id)
        rabbit_producer.publish_data(user_payload)

        refresh_object = await sync_to_async(RefreshToken.objects.create)(user_id=user_id, token=refresh_token)

        return JsonResponse(
            data={
                'type': 'success',
                'access_token': access_token,
                'refresh_token': refresh_object.token
            },
            status=200
        )
    except KeyError as exc:
        return JsonResponse(
            data={
                'type': 'error',
                'details': 'Improper format of data'
            },
            status=400
        )
    except Exception as exc:
        return JsonResponse(
            data={
                'type': 'error',
                'details': exc,
            }
        )

def logout(request: HttpRequest):
    header_value = request.headers.get("Authorization")
    bearer_token = header_value.split(" ")[1]

    redis_manager.block_token('critical')
    request.session.flush()

    return

def refresh_token(request: HttpRequest):
    user_id = request.headers.get("user_id")
    token = RefreshToken.objects.get(user_id)

    return JsonResponse(
        data={
            'type': 'token',
            'token': token.token
        }
    )

def temporary_url(request):
    print("random url")
    return JsonResponse(
        data={
            'success': 'test',
            'esa': 'ok'
        }
    )


async def token_validate_url(request):
    try:

        auth_header = request.headers['Authorization']
        token = auth_header.split(" ")[1]
        valid_token = JWTManager.validate_token(token)
        return JsonResponse(
            data={
                'status': 'succed',
                'data': 'token is valid'
            }
        )
    except Exception as exc:
        return JsonResponse(
            data={
                'type': 'error',
                'details': str(exc)
            }
        )

@never_cache
def render_csrf_token(request):
    csrf_token = get_token(request)

    data = {
        'type1': 'csrfd233',
        'token': csrf_token
    }

    json_data = json.dumps(data, indent=2)
    return HttpResponse(json_data, content_type="application/json")

def ouath2uri(request):
    return {
        'status': 'success',
        'data': 'Test Data'
    }

@csrf_exempt
def login_google(request):
    return render(request, "sign_in.html")

@csrf_exempt
def generate_reset_password_token(request: HttpRequest):
    user_id = request.POST.get("user_id")

    reset_token, payload = JWTManager.generate_reset_token(user_id)
    response = {
        "type": "token",
        "token": reset_token
    }

    reset_token_instance = ResetPasswordToken(
        user=user_id,
        reset_token=reset_token
    )
    reset_token_instance.save()

    return JsonResponse(
        data=response,
        content_type="application/json",
    )

@csrf_exempt
def validate_reset_token(request: HttpRequest):
    token = request.POST.get("token")
    reset_token = ResetPasswordToken.objects.get(token=token)

    if not token:
        raise TokenDoesNotExistError("Token does not exists")

    payload = JWTManager.decode_token(reset_token.token)

    if not reset_token.check_expiration():
        response = create_response_token("token", False)
        return JsonResponse(
            data=response,
            content_type="application/json",
            status=401
        )

    response = create_success_token_response("token", True, payload["user_id"])
    
    return JsonResponse(
        data=response,
        content_type="application/json",
        status=202
    )


