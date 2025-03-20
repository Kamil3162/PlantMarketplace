from .models import Product

def user_delete(user_id):
    product = Product.objects.get(user_id=user_id)
    product.delete()
    return {'success': True}