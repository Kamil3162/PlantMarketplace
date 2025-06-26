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


from microservices_provider import UserClient
from data.models import BlackListedTokens
from mechanism.redis_manager import RedisManager

redis_manager = RedisManager()

user_client = UserClient()
# consul - service discovery
# hystrix pattern
# jwt issui validation
# kong routing loadbalnacing
# in this code i will create instance for making a requests into user-service

# prefix based on authenticate
from mechanism import RedisManager, JWTManager
from data.models import RefreshToken


@csrf_exempt
async def login(request: HttpRequest):
    try:
        path = "/user/email"
        # we hva to create refresh token in our database
        # we have to get user id to we can use a header

        if request.content_type == "application/json":
            data_json = json.loads(request.body.decode('utf-8'))
        else:
            data_json = request.POST

        response = await user_client.make_request(
            path,
            method=request.method,
            json_data=data_json
        )

        # we can create refresh token during login but not every time or maybe yes
        # user_id
        print(response)

        user_data = response['detail']
        user_id = user_data['id']

        access_token = JWTManager.create_access_token(user_id)
        refresh_token = JWTManager.create_refresh_token(user_id)
        # first we can try to fetch that this
        # this code create each time brand new refresh token for each login attemp
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
    # we have to get access token
    header_value = request.headers.get("Authorization")
    bearer_token = header_value.split(" ")[1]

    redis_manager.block_token('critical')
    request.session.flush()
    return

def refresh_token(request: HttpRequest):
    # we have to find this particular user after decode
    # ok first we query postgresql
    user_id = request.headers.get("user_id")
    token = RefreshToken.objects.get(user_id)
    # we get queryset
    return JsonResponse(
        data={
            'type': 'token',
            'token': token.token
        }
    )


def revoke(request: HttpRequest):
    pass


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
    csrf_token = get_token(request)  # ← Poprawna nazwa

    data = {
        'type1': 'csrfd233',
        'token': csrf_token
    }

    json_data = json.dumps(data, indent=2)
    return HttpResponse(json_data, content_type="application/json")