# management/commands/process_user.py
import sys
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Process user with various options"

    def add_arguments(self, parser):
        """Dodawanie argumentów i opcji do komendy"""

        # Argument pozycyjny (wymagany)
        parser.add_argument('user_id', type=int, help='ID użytkownika')

        # Argumenty opcjonalne
        parser.add_argument(
            '--email',
            type=str,
            help='Email użytkownika',
            default=None
        )

        # Flagi boolean
        parser.add_argument(
            '--force',
            action='store_true',
            help='Wymuś wykonanie bez potwierdzenia',
        )

        # Argumenty z wyborem
        parser.add_argument(
            '--format',
            choices=['json', 'csv', 'xml'],
            default='json',
            help='Format eksportu danych'
        )

        # Argumenty z wieloma wartościami
        parser.add_argument(
            '--tags',
            nargs='+',  # + oznacza jeden lub więcej
            help='Lista tagów'
        )

    def handle(self, *args, **options):
        """Główna logika komendy"""
        try:
            # Pobieranie argumentów
            user_id = options['user_id']
            email = options['email']
            force = options['force']
            format_type = options['format']
            tags = options.get('tags', [])  # Domyślnie pusta lista

            # Komunikat o rozpoczęciu
            self.stdout.write(
                self.style.SUCCESS(f'Rozpoczynam przetwarzanie dla użytkownika {user_id}')
            )

            # Wywołanie logiki biznesowej
            result = self.process_user(user_id, email, force, format_type, tags)

            # Komunikat o sukcesie
            self.stdout.write(
                self.style.SUCCESS(f'Pomyślnie zakończono! Wynik: {result}')
            )

        except Exception as e:
            logger.error(f'Błąd w komendzie: {e}')
            raise CommandError(f'Komenda nie powiodła się: {e}')

    def process_user(self, user_id, email, force, format_type, tags):
        """Przetwarzanie użytkownika"""

        # Wyświetl informacje o przetwarzaniu
        self.stdout.write(f'Przetwarzam użytkownika ID: {user_id}')

        if email:
            self.stdout.write(f'Email: {email}')

        if force:
            self.stdout.write(self.style.WARNING('Tryb force włączony!'))

        self.stdout.write(f'Format: {format_type}')

        if tags:
            self.stdout.write(f'Tagi: {", ".join(tags)}')

        # Symulacja przetwarzania
        import time
        time.sleep(1)  # Symulacja pracy

        return f'processed_user_{user_id}_{format_type}'