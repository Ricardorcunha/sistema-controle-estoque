"""
wsgi.py — Entry point para servidores WSGI (Gunicorn, uWSGI).

WSGI = Web Server Gateway Interface.
É o protocolo padrão para comunicação entre servidor web e aplicação Python.
Em produção, o Gunicorn usa este arquivo.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

application = get_wsgi_application()
