#!/usr/bin/env python
"""Narzędzie wiersza poleceń Django dla mikroserwisu email_service."""
import os
import sys
import importlib
from pathlib import Path

def main():
    """Uruchom zadania administracyjne lub dedykowane komendy mikroserwisu."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
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