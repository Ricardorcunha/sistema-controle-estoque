"""
production.py — Configurações exclusivas do ambiente de produção.

Importa tudo de base.py e sobrescreve com configurações seguras para produção.
Todas as variáveis sensíveis vêm de variáveis de ambiente.
"""

from decouple import config, Csv

from .base import *  # noqa: F401, F403

# ------------------------------------------------------------
# Debug DESATIVADO em produção — NUNCA True em prod!
# Expõe informações sensíveis do sistema quando True.
# ------------------------------------------------------------
DEBUG = False

SECRET_KEY = config("SECRET_KEY")

# ------------------------------------------------------------
# Banco de dados PostgreSQL
# ------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="estoque_db"),
        "USER": config("DB_USER", default="estoque_user"),
        "PASSWORD": config("DB_PASSWORD", default="estoque_pass"),
        "HOST": config("DB_HOST", default="db"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

# ------------------------------------------------------------
# Hosts permitidos — apenas domínios reais do seu servidor.
# Separe por vírgula no .env: ALLOWED_HOSTS=seudominio.com,www.seudominio.com
# ------------------------------------------------------------
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())


# ------------------------------------------------------------
# Segurança adicional para HTTPS em produção
# ------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_HSTS_SECONDS = 31536000          # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# ------------------------------------------------------------
# Whitenoise — serve arquivos estáticos sem precisar de Nginx
# Ideal para deploys simples (Render, Railway, Heroku).
# ------------------------------------------------------------
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")  # noqa: F405

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ------------------------------------------------------------
# Email em produção — configure com seu provedor real (SendGrid, SES etc.)
# ------------------------------------------------------------
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="noreply@estoque.com")


# ------------------------------------------------------------
# CORS em produção — apenas origens específicas
# ------------------------------------------------------------
CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv(), default="")
