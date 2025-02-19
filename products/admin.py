from django.contrib import admin
from .models import Product, Inventory

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    pass

# Register your models here.
class InventoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Product, ProductAdmin)
admin.site.register(Inventory, InventoryAdmin)