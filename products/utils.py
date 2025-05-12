import decimal
import json

from django.core.files import File
from django.db.models import FileField
from django.forms.models import model_to_dict

from .models import Product

def user_delete(user_id):
    product = Product.objects.get(user_id=user_id)
    product.delete()
    return {'success': True}

def generate_product_dict(product_instance):
    product_dict = model_to_dict(product_instance)
    return product_dict

class CustomProductEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o)
        elif isinstance(o, (File, FileField)):
            return str(o) if o else None
        return super().default(o)

