"""
api_views.py — ViewSets da API para Fornecedor.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from apps.api.permissions import IsAdminOrReadOnly

from .models import Fornecedor
from .serializers import FornecedorSerializer


class FornecedorViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para Fornecedor.

    Filtros disponíveis:
        - Por status ativo: /api/v1/fornecedores/?ativo=true
        - Busca por nome/cnpj/email: /api/v1/fornecedores/?search=tech
        - Ordenação: /api/v1/fornecedores/?ordering=-criado_em
    """

    queryset = Fornecedor.objects.all()
    serializer_class = FornecedorSerializer
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["ativo"]
    search_fields = ["nome", "cnpj", "email"]
    ordering_fields = ["nome", "criado_em"]
    ordering = ["nome"]
