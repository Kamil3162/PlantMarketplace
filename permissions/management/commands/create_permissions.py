import sys

from django.core.management import BaseCommand
from django.contrib.auth.models import Permission, ContentType
from account.models import CustomUser

class Command(BaseCommand):
    help = 'Creates permissions for CustomerUser model'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='Permission name')
        parser.add_argument('--codename', type=str, help='Permission codename')

    def handle(self, *args, **options):
        try:
            name = options['name']
            code_name = options['codename']
            permission = Permission.objects.get(name=name)

            if permission:
                self.stdout.write(
                    self.style.WARNING(
                        f'Permission with codename {code_name} already exists'
                    )
                )
                return

            content_type = ContentType.objects.get_for_model(CustomUser)

            # permission automatily invoke save function during create brand new instance
            permission_new = Permission.objects.create(
                name=name,
                content_type=content_type,
                code_name=code_name,
            )

            self.stdout.write(f'Successfully created permission: {name}')
            return
        except Exception as e:
            raise Exception(str(e))