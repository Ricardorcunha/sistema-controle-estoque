"""
base.py — Configurações comuns a todos os ambientes.

Princípio: DRY (Don't Repeat Yourself).
Tudo que é igual em dev e prod fica aqui.
Cada ambiente (development.py, production.py) importa daqui e sobrescreve apenas o necessário.
"""

import os
from pathlib import Path

from decouple import config

# ------------------------------------------------------------
# Caminhos base do projeto
# BASE_DIR aponta para a raiz do repositório (onde está manage.py)
# ------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ------------------------------------------------------------
# Segurança
# NUNCA deixe a SECRET_KEY hardcoded no código.
# Ela vem do arquivo .env via python-decouple.
# ------------------------------------------------------------
SECRET_KEY = config("SECRET_KEY")

# ------------------------------------------------------------
# Aplicações instaladas
# Separadas em grupos para facilitar leitura e manutenção.
# ------------------------------------------------------------
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "django_filters",
    "corsheaders",
]

LOCAL_APPS = [
    "apps.core",
    "apps.usuarios",        # DEVE vir antes de qualquer app que use AUTH_USER_MODEL
    "apps.categorias",
    "apps.fornecedores",
    "apps.produtos",
    "apps.movimentacoes",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS


# ------------------------------------------------------------
# Middlewares
# A ordem importa! corsheaders.middleware.CorsMiddleware
# deve ficar ANTES do CommonMiddleware.
# ------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",       # CORS — deve ser cedo na lista
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ------------------------------------------------------------
# URLs e WSGI/ASGI
# ------------------------------------------------------------
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# ------------------------------------------------------------
# Templates
# O Django procura templates na pasta "templates" de cada app
# e também na pasta "templates" global (aqui configurada).
# ------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # templates globais
        "APP_DIRS": True,                  # também busca em cada app/templates/
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# ------------------------------------------------------------
# Banco de dados
# Configurado via variáveis de ambiente para não expor credenciais.
# ------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="estoque_db"),
        "USER": config("DB_USER", default="estoque_user"),
        "PASSWORD": config("DB_PASSWORD", default="estoque_pass"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}


# ------------------------------------------------------------
# Validação de senhas
# ------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ------------------------------------------------------------
# Internacionalização
# ------------------------------------------------------------
LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True


# ------------------------------------------------------------
# Arquivos estáticos e de mídia
# ------------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # onde collectstatic coloca os arquivos em prod
STATICFILES_DIRS = [BASE_DIR / "static"]  # pasta de estáticos do projeto

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ------------------------------------------------------------
# Modelo de usuário customizado
# DEVE ser definido antes das migrations que referenciam usuário.
# Após definir, não pode ser trocado sem recriar o banco.
# ------------------------------------------------------------
AUTH_USER_MODEL = "usuarios.Usuario"

# URLs de redirecionamento de autenticação
LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/"       # Após login bem-sucedido
LOGOUT_REDIRECT_URL = "/login/"  # Após logout

# ------------------------------------------------------------
# Chave primária padrão
# BigAutoField usa BIGINT no banco — melhor para sistemas grandes.
# ------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ------------------------------------------------------------
# Django REST Framework — configurações globais
# ------------------------------------------------------------
REST_FRAMEWORK = {
    # Handler global de exceções customizado
    "EXCEPTION_HANDLER": "apps.core.exception_handler.custom_exception_handler",
    # Autenticação padrão: JWT
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",  # para o Browsable API
    ],
    # Permissão padrão: deve estar autenticado
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    # Paginação padrão
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    # Filtros
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    # Schema para Swagger
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


# ------------------------------------------------------------
# JWT — Simple JWT
# ------------------------------------------------------------
from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "AUTH_HEADER_TYPES": ("Bearer",),
}


# ------------------------------------------------------------
# drf-spectacular — configuração do Swagger
# ------------------------------------------------------------
SPECTACULAR_SETTINGS = {
    "TITLE": "Sistema de Controle de Estoque — API",
    "DESCRIPTION": (
        "API REST completa para gerenciamento de estoque. "
        "Permite cadastrar produtos, categorias, fornecedores "
        "e registrar movimentações de entrada e saída."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}


# ------------------------------------------------------------
# CORS — permitir que o React (frontend separado) consuma a API
# Os valores específicos ficam nos settings de cada ambiente.
# ------------------------------------------------------------
CORS_ALLOWED_ORIGINS: list[str] = []


# ------------------------------------------------------------
# Logging básico — será expandido nas próximas etapas
# ------------------------------------------------------------
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOGS_DIR / "app.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 5,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "apps": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
    },
}
