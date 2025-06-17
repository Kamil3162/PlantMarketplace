import os
import json

from dotenv import load_dotenv

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login, logout
from google.oauth2 import id_token
from google.auth.transport import requests
from django.core.serializers import serialize

from account.forms import RegisterForm, LoginForm
from core.redis_manager import RedisManager
from core.jwt_manager import JWTManager
from core.utils import remove_access_token, black_token_validation
from permissions.models import PermissionGroupAssigment
from .utils import auth_decorator


load_dotenv()
redis_manager = RedisManager()

@csrf_exempt
def sign_in(request):
    print(request.session.get('user_data'))
    form = LoginForm()
    return render(request, 'sign_in.html', {'form': form})

def login(request):
    if request.method == 'POST':
        response = HttpResponse('Cookie Set')
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        token = redis_manager.assign_user(user)

        # set a cookie named access_token with a value 'access_token
        response.headers['Authorization'] = f'Bearer {token}'

        response.set_cookie(
            'access_token',
            token,
            max_age=3600,
            httponly=True
        )

        return response

@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    token = request.POST['credential']

    try:
        user_data = id_token.verify_oauth2_token(
            token, requests.Request(), os.environ['GOOGLE_OAUTH_CLIENT_ID']
        )
    except ValueError:
        return HttpResponse(status=403)

    # In a real app, I'd also save any new user here to the database.
    # You could also authenticate the user here using the details from Google (https://docs.djangoproject.com/en/4.2/topics/auth/default/#how-to-log-a-user-in)
    request.session['user_data'] = user_data

    return redirect('sign_in')

@remove_access_token
def sign_out(request):
    print('sign out request')
    try:
        request.session.flush()
        del request.session['user_data']
    except KeyError:
        print('request doesnt have field user_data')
    response = redirect('sign_in')
    response.delete_cookie('access_token')

    return response



# @authenticated(api_response=True)
@auth_decorator(redirect_url='sign_in', api_response=False)
def url_test(request):
    return HttpResponse({
        'message': 'test message',
        'user_email': request.session.get('user_data'),
        'status': 'authenticated'
    })

@black_token_validation
def get_cookie_value(request):
    request_headers = request.headers
    print('HTTP_AUTHORIZATION'.upper() in request.META.keys())
    print(request_headers.get('Authorization', None))
    access_token = request.COOKIES.get('access_token', 'Cookie not found')

    redis_client = redis_manager.get_user_data(access_token)
    token_decoded = JWTManager.decode_token(access_token)
    return HttpResponse(
        json.dumps(token_decoded)
    )

