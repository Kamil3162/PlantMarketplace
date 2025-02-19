from django.db import models
from account.models import User
from products.models import Product

# Create your models here.
class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('finilized', 'Finilized'),
        ('pending', 'Pending'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.UUIDField
    quantity = models.IntegerField(default=1)
    final_price = models.FloatField()
