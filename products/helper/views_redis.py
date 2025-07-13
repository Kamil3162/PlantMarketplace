from django.http.response import JsonResponse

from redis_microservices import client


def redis_test_get(request):
    redis_client = client()
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
    redis_client = client()
    data = redis_client.delete_product('test')

    return JsonResponse(data={
        'status': 'succes',
        'data': 'test'
    })

