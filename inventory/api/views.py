import json

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async

from data.models import Inventory
from microservices_provider import ProductClient
product_client = ProductClient()

def get_content_type(request: HttpRequest):
    request_content_type = request.headers.get(
        'content_type'
    )
    return request_content_type

def base_view(request):
    return JsonResponse(
        data={
            'status': 'success',
            'data': 'random_data',
        }
    )

@csrf_exempt
async def create_inventory(request: HttpRequest):
    try:
        if request.method != "POST":
            return JsonResponse(
                data={
                    'error': 'method',
                    'detail': 'Method forbidden'
                },
                status=403
            )
        test_uuid = "651682dc-6202-43e7-b793-caba6a6de3d9"
        product_uuid = request.POST.get('product_id')
        product_json_response = await product_client.make_request(
            f"product/{test_uuid}/"
        )

        print(dict(product_json_response))
        print(request.POST)
        print(product_json_response)
        print(product_json_response.status_code)
        print(product_json_response.content)
        print(product_json_response.text)

    except Exception as e:
        print(e)

@csrf_exempt
def reserve_inventory(request: HttpRequest):
    content_type = get_content_type(request)

    if request.method == "POST":
        if content_type == 'application/json':
            data = json.loads(request.POST)
            product_id = data['product_id']


