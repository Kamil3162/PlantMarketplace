import time
from functools import wraps

from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect

import logging

logger = logging.getLogger(__name__)

def auth_decorator(redirect_url='sign_in', api_response=False):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                user_data = request.session.get('user_data')
                if not user_data:
                    return redirect(redirect_url)

                expiration_time = user_data.get('exp')
                current_time = time.time()
                rest_time = (expiration_time - current_time) // 60
                if rest_time < 0:
                    del request.session['user_data']
                    return redirect(redirect_url)
            except KeyError:
                return redirect(redirect_url)

            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator