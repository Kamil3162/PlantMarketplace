import json
import os
from dotenv import load_dotenv

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.contrib.auth import authenticate, login, logout
from google.oauth2 import id_token
from google.auth.transport import requests

from .utils import auth_decorator
from account.forms import RegisterForm, LoginForm
from account.scheme import UserScheme
from core.redis_manager import RedisManager
from core.jwt_manager import JWTManager

load_dotenv()
redis_manager = RedisManager()

@csrf_exempt
def sign_in(request):
    print(request.session.get('user_data'))
    form = LoginForm()
    return render(request, 'sign_in.html', {'form': form})

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email, password=password)
        token = redis_manager.assign_user(user)

        return HttpResponse(token)

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

def sign_out(request):
    del request.session['user_data']
    return redirect('sign_in')

def register(request):
    """
        Function responsible for registering a new user

        :param request:
        :return:
    """
    if request.method == 'POST':
        data = request.POST
        form = RegisterForm(data)
        try:
            if form.is_valid():
                user = form.save()
                user_dict = model_to_dict(user, fields=[
                    'id',
                    'first_name',
                    'last_name',
                    'email',
                    'is_active'
                ])
                return JsonResponse({
                    'status': 'success',
                    'user_data': user_dict
                })
        except ValidationError as e:
            raise ValidationError(str(e))
        return HttpResponse('hello post method')
    else:
        form = RegisterForm()
        return render(request, 'register.html', {'form': form})

# @authenticated(api_response=True)
@auth_decorator(redirect_url='sign_in', api_response=False)
def url_test(request):
    return HttpResponse({
        'message': 'test message',
        'user_email': request.session.get('user_data'),
        'status': 'authenticated'
    })

