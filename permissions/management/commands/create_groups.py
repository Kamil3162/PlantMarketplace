from django.core.management import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create groups for builtin Group model'

    def add_arguments(self, parser):
        parser.add_argument('--name', type=str, help='Group name')

    def handle(self, *args, **options):
        try:
            group_name = options['name']
            group = Group.objects.get(name=group_name)

            if group:
                self.stdout.write(f'Group:{group_name} already exists')
                return

        except Exception as e:
            self.stdout.write(f'Group:{group_name} does not exist')





