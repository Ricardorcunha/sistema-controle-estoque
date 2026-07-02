"""
urls.py — Router central da API v1.

DefaultRouter registra automaticamente todas as rotas dos ViewSets:
    /api/v1/categorias/           → list, create
    /api/v1/categorias/{id}/      → retrieve, update, destroy
    /api/v1/produtos/abaixo-do-minimo/ → action customizada
    etc.

Versionamento:
    Prefixo /api/v1/ desde o início. Quando precisarmos de mudanças
    incompatíveis, criamos /api/v2/ sem quebrar os clientes existentes.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from apps.categorias.api_views import CategoriaViewSet
from apps.fornecedores.api_views import FornecedorViewSet
from apps.produtos.api_views import ProdutoViewSet
from apps.movimentacoes.api_views import MovimentacaoViewSet
from apps.usuarios.api_views import UsuarioViewSet

# DefaultRouter gera automaticamente as URLs REST para cada ViewSet
router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categorias")
router.register("fornecedores", FornecedorViewSet, basename="fornecedores")
router.register("produtos", ProdutoViewSet, basename="produtos")
router.register("movimentacoes", MovimentacaoViewSet, basename="movimentacoes")
router.register("usuarios", UsuarioViewSet, basename="usuarios")

urlpatterns = [
    # Todos os endpoints do router
    path("", include(router.urls)),

    # JWT Authentication
    # POST /api/v1/auth/token/         → recebe {username, password} → retorna {access, refresh}
    # POST /api/v1/auth/token/refresh/ → recebe {refresh} → retorna novo {access}
    # POST /api/v1/auth/token/verify/  → recebe {token} → valida se é válido
    path("auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("auth/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
