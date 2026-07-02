"""
urls.py — Roteamento principal do projeto.

Boas práticas:
- Cada app tem seu próprio urls.py e é incluído aqui com include().
- A API fica sob o prefixo /api/v1/ — versionamento desde o início.
- Swagger e Redoc ficam disponíveis apenas em DEBUG.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Admin do Django
    path("admin/", admin.site.urls),

    # Documentação da API (Swagger / Redoc)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),

    # Autenticação (web)
    path("", include("apps.usuarios.urls")),

    # Frontend web — CRUDs
    path("", include("apps.core.urls")),
    path("categorias/", include("apps.categorias.urls")),
    path("fornecedores/", include("apps.fornecedores.urls")),
    path("produtos/", include("apps.produtos.urls")),
    path("movimentacoes/", include("apps.movimentacoes.urls")),

    # API REST v1
    path("api/v1/", include("apps.api.urls")),
]

# Em desenvolvimento, servir arquivos de mídia
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
