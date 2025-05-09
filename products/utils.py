import decimal
import json

from django.core.files import File
from django.db.models import FileField

from .models import Product

def user_delete(user_id):
    product = Product.objects.get(user_id=user_id)
    product.delete()
    return {'success': True}

class CustomProductEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return int(o)
        elif isinstance(o, (File, FileField)):
            return str(o) if o else None
        return super().default(o)

