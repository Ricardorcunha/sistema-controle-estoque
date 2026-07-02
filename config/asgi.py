"""
asgi.py — Entry point para servidores ASGI (Daphne, Uvicorn).

ASGI = Asynchronous Server Gateway Interface.
Permite requisições assíncronas (WebSockets, HTTP/2).
Preparamos o projeto para suportar WebSockets no futuro (ex: notificações em tempo real).
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

application = get_asgi_application()
