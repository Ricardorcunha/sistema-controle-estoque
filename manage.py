#!/usr/bin/env python
"""
manage.py — Utilitário de linha de comando do Django.

Uso:
    python manage.py runserver
    python manage.py migrate
    python manage.py createsuperuser
    python manage.py shell
    etc.

O settings padrão aponta para 'development'.
Em produção, defina a variável de ambiente:
    DJANGO_SETTINGS_MODULE=config.settings.production
"""

import os
import sys


def main() -> None:
    """Ponto de entrada principal do Django CLI."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Não foi possível importar o Django. Verifique se ele está "
            "instalado e disponível no PYTHONPATH. Se estiver usando "
            "virtualenv, certifique-se de que está ativado."
        ) from exc

    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
