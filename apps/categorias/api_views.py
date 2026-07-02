"""
api_views.py — ViewSets da API para Categoria.

ModelViewSet gera automaticamente todos os endpoints:
  GET    /categorias/       → list()
  POST   /categorias/       → create()
  GET    /categorias/{id}/  → retrieve()
  PUT    /categorias/{id}/  → update()
  PATCH  /categorias/{id}/  → partial_update()
  DELETE /categorias/{id}/  → destroy()
"""

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.api.permissions import IsAdminOrReadOnly

from .models import Categoria
from .serializers import CategoriaSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para Categoria.

    Permissões:
        - Leitura (GET): qualquer usuário autenticado
        - Escrita (POST/PUT/DELETE): apenas admins

    Filtros disponíveis:
        - Busca por nome: /api/v1/categorias/?search=eletro
        - Ordenação: /api/v1/categorias/?ordering=nome
    """

    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    # Campos que o DRF usa para a busca (?search=...)
    search_fields = ["nome", "descricao"]

    # Campos que o usuário pode ordenar (?ordering=nome)
    ordering_fields = ["nome", "criado_em"]
    ordering = ["nome"]  # Ordenação padrão
