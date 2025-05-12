import json
from django.http.response import JsonResponse

from redis_microservices import redis_product_client
from .utils import CustomProductEncoder

def redis_test_get(request):
    redis_client = redis_product_client()
    data = redis_client.insert_db_products()
    product_keys = redis_client.fetch_all()
    print(product_keys)
    return JsonResponse(data={
        'status': 'fine',
        'data': product_keys
    })


def redis_test_delete(request):
    print(request)
    print(request.GET.get('ID'))
    redis_client = redis_product_client()
    data = redis_client.delete_product('test')

    return JsonResponse(data={
        'status': 'succes',
        'data': 'test'
    })

