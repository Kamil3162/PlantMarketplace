from django.db import models
from account.models import User
from plant_marketplace import settings

# Create your models here.
import uuid
# wariagacja / liscie
# ziemia / rodzaj
# kategoryzacja
# bezpiecznie dla zwierzat

class Product(models.Model):
    SUNLIGHT_CHOICES = [
        ('full', 'Full Sun'),
        ('partial', 'Partial Sun'),
        ('shade', 'Shade')
    ]

    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard')
    ]

    WATER_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High')
    ]

    id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    name = models.CharField(max_length=100)
    scientific_name = models.CharField(max_length=100, blank=True)
    description = models.TextField(max_length=500, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Plant Care Details
    sunlight = models.CharField(max_length=20, choices=SUNLIGHT_CHOICES)
    water_needs = models.CharField(max_length=20, choices=WATER_CHOICES)
    care_difficulty = models.CharField(max_length=20,
                                       choices=DIFFICULTY_CHOICES)

    # Physical Characteristics
    height = models.DecimalField(max_digits=5, decimal_places=2,
                                 help_text="Height in cm")
    spread = models.DecimalField(max_digits=5, decimal_places=2,
                                 help_text="Spread in cm")
    bloom_time = models.CharField(max_length=50, blank=True)
    flower_color = models.CharField(max_length=50)

    # Stock and Status
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # Optional Image field (requires Pillow package)
    image = models.ImageField(upload_to='flowers/', blank=True, null=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Flower'
        verbose_name_plural = 'Flowers'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('flower-detail', args=[str(self.id)])


class Inventory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_id = models.UUIDField()
    quantity = models.PositiveIntegerField(default=0)
    low_stock_treshold = models.PositiveIntegerField(default=5)
    reserved_quantity = models.PositiveIntegerField(default=0)

    def get_aviable_quantity(self):
        return self.quantity - self.reserved_quantity

