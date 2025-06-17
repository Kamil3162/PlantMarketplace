
from django.http import JsonResponse

def base_view(request):
    return JsonResponse(
        data={
            'status': 'success',
            'data': 'random_data',
        }
    )