from django.apps import AppConfig
from django.db.models.signals import post_migrate


class PermissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "permissions"

    def ready(self):

        post_migrate.connect(self.create_permissions, sender=self)

    def create_permissions(self, sender, **kwargs):
        try:
            from .models import PermissionGroupAssigment

            permissions = PermissionGroupAssigment.objects._create_permissions()
            group_list = PermissionGroupAssigment.objects._generate_base_groups()

        except Exception as e:
            raise Exception(str(e))