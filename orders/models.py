from django.db import models
from account.models import CustomUser
from products.models import Product

# Create your models here.
class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('finilized', 'Finilized'),
        ('pending', 'Pending'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=ORDER_STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    final_price = models.FloatField()

    @property
    def calculated_price(self):
        return self.quantity * self.product.price


class OrderEvent(models.Model):
    EVENTS = (
        ('created', 'Created'),
        ('updated', 'Updated'),
        ('fullfilled', 'Fullfilled'),
        ('refunded', 'Refunded'),
    )

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    event = models.CharField(max_length=30, choices=EVENTS, default='created')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('event',)