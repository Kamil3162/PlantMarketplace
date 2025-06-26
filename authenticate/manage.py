#!/usr/bin/env python
"""Narzędzie wiersza poleceń Django dla mikroserwisu email_service."""
import os
import sys
import importlib
from pathlib import Path

# Ścieżka do katalogu z komendami
COMMANDS_DIR = Path(__file__).parent / 'management' / 'commands'


def main():
    """Uruchom zadania administracyjne lub dedykowane komendy mikroserwisu."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

    # Obsługa komend standardowych Django
    if len(sys.argv) <= 1 or sys.argv[1] in ['-h', '--help', 'help']:
        try:
            from django.core.management import execute_from_command_line
            execute_from_command_line(sys.argv)
            return
        except ImportError as exc:
            raise ImportError(
                "Nie można zaimportować Django. Sprawdź, czy jest zainstalowane."
            ) from exc

    # Obsługa dedykowanych komend mikroserwisu
    command_name = sys.argv[1]
    command_file = COMMANDS_DIR / f"{command_name}.py"

    print(command_file)
    print("test test tesst")

    # Sprawdź, czy istnieje dedykowany plik komendy
    if command_file.exists():
        print("commands exists")
        try:
            # Inicjalizacja Django
            import django
            django.setup()

            # Dynamiczne importowanie modułu komendy
            module_path = f"management.commands.{command_name}"
            command_module = importlib.import_module(module_path)

            # Sprawdź, czy moduł zawiera klasę Command
            if hasattr(command_module, 'Command'):
                # Użyj klasy Command jeśli istnieje (kompatybilność z Django)
                command_class = getattr(command_module, 'Command')
                command = command_class()
                command.handle(*sys.argv[2:])
            elif hasattr(command_module, 'execute'):
                # Alternatywnie, użyj funkcji execute jeśli istnieje
                execute_func = getattr(command_module, 'execute')
                execute_func(*sys.argv[2:])
            else:
                # Ostateczność: zaimportuj cały moduł, który powinien wykonać potrzebne operacje
                print(f"Uruchamianie komendy mikroserwisu: {command_name}")
                print("Zakończono wykonanie komendy.")

            return
        except Exception as e:
            print(f"Błąd podczas wykonywania komendy {command_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    # Jeśli nie znaleziono dedykowanej komendy, użyj standardowego mechanizmu Django
    try:
        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
    except ImportError as exc:
        raise ImportError(
            "Nie można zaimportować Django. Sprawdź, czy jest zainstalowane."
        ) from exc
    except Exception as e:
        print(f"Błąd podczas wykonywania komendy Django: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()