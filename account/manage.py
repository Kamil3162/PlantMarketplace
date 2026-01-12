#!/usr/bin/env python
"""Narzędzie wiersza poleceń Django dla mikroserwisu email_service."""
import os
import sys
import importlib
from pathlib import Path
import consul


COMMANDS_DIR = Path(__file__).parent / 'management' / 'commands'


consul_connection = consul.Consul(
    host='localhost',
    port=8500,
)


def register_with_consul():
    import socket

    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)

    c = consul.Consul(
        host='consul1',
        port=8500,
    )

    c.agent.service.register(
        name="user-service",
        service_id=f"user-service",
        address="user-service",
        port=8001,
        tags=['web', 'account'],
        check=consul.Check.http(
            "http://user-service:8001/health",
            interval="50s"
        ),
    )


def execute_command(
    std_input: str = None,
    command: str = None,
    command_path: str = None
):
    try:
        command = std_input[1]
        command_file = COMMANDS_DIR / f"{command}.py"

        if command_file.exists():
            module_path = f"management.commands.{command}"
            command_module = importlib.import_module(module_path)

            if hasattr(command_module, "Command"):
                command_class = getattr(command_module, "Command")
                command_instance = command_class()
                command_instance.execute()
            return

    except Exception as e:
        print(f"Błąd podczas wykonywania komendy {command}: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def main():
    try:
        from django.core.management import execute_from_command_line
        import django

        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()

        if len(sys.argv) <= 1 or sys.argv[1] in ['-h', '--help', 'help']:
            try:
                from django.core.management import execute_from_command_line
                execute_from_command_line(sys.argv)
                return
            except ImportError as exc:
                raise ImportError(
                    "Nie można zaimportować Django. Sprawdź, czy jest zainstalowane."
                ) from exc

        command_name = sys.argv[1]
        command_file = COMMANDS_DIR / f"{command_name}.py"
        execute_command(sys.argv, command_name, command_file)

        register_with_consul()
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