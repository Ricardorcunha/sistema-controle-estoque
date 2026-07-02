"""
api_views.py — ViewSets da API para Produto.

Inclui actions customizadas:
    - abaixo_do_minimo: lista produtos com estoque crítico
    - sem_estoque: lista produtos zerados
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.api.permissions import IsAdminOrReadOnly
from apps.movimentacoes.services import EstoqueService

from .models import Produto
from .serializers import ProdutoSerializer, ProdutoDetalheSerializer


class ProdutoViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para Produto.

    Actions customizadas:
        GET /api/v1/produtos/abaixo_do_minimo/ → produtos em alerta
        GET /api/v1/produtos/sem_estoque/      → produtos zerados

    Filtros:
        ?ativo=true
        ?categoria=1
        ?fornecedor=2
        ?search=notebook
        ?ordering=nome
    """

    queryset = Produto.objects.select_related(
        "categoria", "fornecedor"
    ).all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["ativo", "categoria", "fornecedor"]
    search_fields = ["nome", "categoria__nome", "fornecedor__nome"]
    ordering_fields = ["nome", "preco", "quantidade_atual", "criado_em"]
    ordering = ["nome"]

    def get_serializer_class(self):
        """
        Retorna serializer diferente para leitura vs escrita.

        GET  → ProdutoDetalheSerializer (dados aninhados)
        POST/PUT/PATCH → ProdutoSerializer (IDs simples)

        Isso é o padrão "dual serializer" no DRF.
        """
        if self.action in ("list", "retrieve"):
            return ProdutoDetalheSerializer
        return ProdutoSerializer

    @action(detail=False, methods=["get"], url_path="abaixo-do-minimo")
    def abaixo_do_minimo(self, request: Request) -> Response:
        """
        Lista produtos com estoque abaixo do mínimo.
        GET /api/v1/produtos/abaixo-do-minimo/

        @action cria um endpoint extra além dos padrões do ModelViewSet.
        detail=False: endpoint de lista (não precisa de {id})
        """
        service = EstoqueService()
        queryset = service.produtos_abaixo_do_minimo()
        serializer = ProdutoDetalheSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response({
            "count": queryset.count(),
            "results": serializer.data,
        })

    @action(detail=False, methods=["get"], url_path="sem-estoque")
    def sem_estoque(self, request: Request) -> Response:
        """
        Lista produtos sem estoque (quantidade = 0).
        GET /api/v1/produtos/sem-estoque/
        """
        service = EstoqueService()
        queryset = service.produtos_sem_estoque()
        serializer = ProdutoDetalheSerializer(
            queryset, many=True, context={"request": request}
        )
        return Response({
            "count": queryset.count(),
            "results": serializer.data,
        })
