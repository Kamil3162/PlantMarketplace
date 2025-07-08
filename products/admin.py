from django.contrib import admin
from data.models import Product, Inventory, InventoryEvent

# Register your models here.
class ProductAdmin(admin.ModelAdmin):
    pass

# Register your models here.
class InventoryAdmin(admin.ModelAdmin):
    pass

admin.site.register(Product, ProductAdmin)
admin.site.register(Inventory, InventoryAdmin)
admin.site.register(InventoryEvent, InventoryAdmin)

"""
    log_path = Path(os.getcwd()).parent
    
    s3_client = S3Client(
        access_key=os.environ.get("AWS_ACCESS"),
        secret_key=os.environ.get("AWS_SECRET"),
        region=os.environ.get("AWS_REGION"),
        bucket_name=os.environ.get("AWS_BUCKET_NAME"),
        logs_path=log_path
    )
    bucket_name = os.environ.get("AWS_BUCKET_NAME")
    
    print(s3_client.list_buckets())
    print(s3_client.show_files_from_bucket(bucket_name))
"""