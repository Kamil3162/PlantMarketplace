import json

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from asgiref.sync import sync_to_async
from django.core.exceptions import ValidationError

from data.models import Inventory, InventoryEvent, ReservedInventory
from microservices_provider import ProductClient
from django.views.decorators.http import require_http_methods
from django.forms.models import model_to_dict

product_client = ProductClient()
EVENTS = InventoryEvent.EVENT_CHOICES


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
        quantity = request.POST.get('quantity')
        low_stock_threshold = request.POST.get('low_stock_threshold')
        user_uuid = request.headers.get('Marketplace-User')

        product_json_response = await product_client.make_request(
            f"product/{test_uuid}/"
        )

        if product_json_response.status == 200:
            product_json_data = await json.loads(product_json_response)
            product_uuid = product_json_data['uuid']

            inventory = Inventory.objects.create_inventory(
                product=product_uuid,
                quantity=quantity,
                low_stock_threshold=low_stock_threshold
            )

            InventoryEvent.objects.create(
                inventory=inventory,
                user=user_uuid,
                event=InventoryEvent.EVENT_CREATED
            )

    except Exception as e:
        return JsonResponse(
            data={
                'type': 'error',
                'detail': str(e),
            },
            status=500
        )


@csrf_exempt
@require_http_methods(["POST"])
async def reserve_inventory(request: HttpRequest):
    try:
        content_type = get_content_type(request)
        user_uuid = request.headers.get('Marketplace-User')

        if not user_uuid:
            raise ValidationError("User not found")

        if content_type == 'application/json':
            data = json.loads(request.body)
            product_uuid = data['product_id']
            quantity = data['quantity']
        else:
            product_uuid = request.POST.get('product_id')
            quantity = request.POST.get('quantity', 1)

        if not product_uuid:
            raise ValidationError("Product not found")

        if quantity <= 0:
            raise ValidationError("Quantity must be greater than 0")

        product_json_response = await product_client.make_request(
            f"product/{product_uuid}/"
        )

        if product_json_response.status != 200:
            raise ValidationError("Product not found")

        product_response = await json.loads(product_json_response)
        product_uuid = product_response['uuid']

        inventory = await Inventory.objects.select_for_update().aget(
            product=product_uuid
        )

        if not inventory:
            raise ValidationError("Following inventory product does not exists")

        existing_reservation = await ReservedInventory.objects.filter(
            inventory=inventory,
            user=user_uuid,
        ).aexists()

        if existing_reservation:
            raise ValidationError("Reservation already exists for this user")

        reserved_object = await ReservedInventory.objects.acreate(
            inventory=inventory,
            quantity=quantity,
            refernce="test",
            user=user_uuid,
        )

        return JsonResponse(
            data={
                'type': 'success',
                'message': "Product successfully reserved",
                'detail': {
                    'reservation_id': str(reserved_object.id),
                    'product_id': product_uuid,
                    'quantity': quantity,
                    'reference': reserved_object.reference
                }
            },
            status=201
        )

    except Inventory.DoesNotExist as e:
        return JsonResponse(
            data={
                'type': 'error',
                'detail': str(e),
            },
            status=404
        )
    except Exception as e:
        return JsonResponse(
            data={
                'type': 'error',
                'detail': str(e),
            },
            status=500
        )


def base_view(request):
    return JsonResponse(
        data={
            'status': 'success',
            'data': 'random_data',
        }
    )

def get_inventory(request: HttpRequest, sku: str):
    """GET /inventory/{sku} - stan magazynowy"""
    pass

def check_availability(request: HttpRequest):
    """POST /inventory/check - bulk check dostępności"""
    # body: {"items": [{"sku": "XXX", "quantity": 2}]}
    pass

def get_bulk_inventory(request: HttpRequest):
    """POST /inventory/bulk - pobranie stanów wielu SKU"""
    # body: {"skus": ["sku1", "sku2", "sku3"]}
    pass

def confirm_reservation(request: HttpRequest, reservation_id: str):
    """POST /reservations/{id}/confirm - potwierdź po płatności"""
    pass

def reserve_products(request: HttpRequest):
    """Każda operacja write powinna mieć idempotency_key"""
    # Headers: X-Idempotency-Key: uuid
    # Zapobiega duplikatom przy retry

def atomic_multi_reserve(request: HttpRequest):
    """Rezerwuj wiele SKU - wszystko albo nic"""
    # Jeśli choć jeden SKU niedostępny - rollback całości
    # Krytyczne dla koszyków z wieloma produktami

# Background job/cron co minutę
def cleanup_expired_reservations():
    """Automatyczne zwalnianie wygasłych rezerwacji"""
    pass

def extend_reservation(request: HttpRequest, reservation_id: str):
    """POST /reservations/{id}/extend - przedłuż TTL"""
    pass

def get_reservation_status(request: HttpRequest, reservation_id: str):
    """GET /reservations/{id} - status rezerwacji"""
    pass

def adjust_inventory(request: HttpRequest):
    """POST /inventory/adjust - korekta stanu (admin)"""
    # reason: damage, loss, found, manual_correction
    pass

def bulk_update(request: HttpRequest):
    """POST /inventory/bulk-update - masowa aktualizacja"""
    pass

def receive_stock(request: HttpRequest):
    """POST /inventory/receive - przyjęcie dostawy"""
    pass

def transfer_between_locations(request: HttpRequest):
    """POST /inventory/transfer - między lokalizacjami"""
    pass

def get_low_stock_items(request: HttpRequest):
    """GET /inventory/alerts/low-stock"""
    pass

def get_inventory_metrics(request: HttpRequest):
    """GET /inventory/metrics - dla dashboardów"""
    pass

def inventory_webhook_status(request: HttpRequest):
    """GET /inventory/webhooks - status webhooków"""
    pass


def create_inventory_snapshot(request: HttpRequest):
    """POST /inventory/snapshot - dla inwentaryzacji"""
    # Zapisz stan całego inventory w czasie T


def get_inventory_history(request: HttpRequest, sku: str):
    """GET /inventory/{sku}/history - audit trail"""
    pass



def first_request(request: HttpRequest):
    return {
        'esa': 'value'
    }
