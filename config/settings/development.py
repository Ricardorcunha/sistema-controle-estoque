"""
development.py — Configurações exclusivas do ambiente de desenvolvimento.

Importa tudo de base.py e sobrescreve apenas o necessário.
NUNCA use este arquivo em produção.
"""

import socket
from .base import *  # noqa: F401, F403

# ------------------------------------------------------------
# Debug ATIVO em desenvolvimento
# Mostra stack traces detalhados no browser quando há erro.
# ------------------------------------------------------------
DEBUG = True

# ------------------------------------------------------------
# Hosts permitidos em desenvolvimento
# '*' aceita qualquer host — apenas em dev, nunca em prod!
# ------------------------------------------------------------
ALLOWED_HOSTS = ["*"]


# ------------------------------------------------------------
# Django Debug Toolbar
# Ferramenta poderosa para inspecionar queries SQL,
# templates carregados, cache, sinais etc.
# ------------------------------------------------------------
# Debug Toolbar — desabilitado temporariamente (reativar com Docker)
# INSTALLED_APPS += ["debug_toolbar"]
# MIDDLEWARE += ["debug_toolbar.middleware.DebugToolbarMiddleware"]


# ------------------------------------------------------------
# Email — em dev, imprime no console em vez de enviar
# ------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"


# ------------------------------------------------------------
# CORS em desenvolvimento — permite o React local (porta 3000)
# ------------------------------------------------------------
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",   # Vite dev server (React)
    "http://127.0.0.1:5173",
]

# Em dev, podemos ser mais permissivos com cookies CSRF
CORS_ALLOW_CREDENTIALS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
