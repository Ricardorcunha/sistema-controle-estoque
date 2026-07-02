"""
api_views.py — ViewSets da API para Movimentacao.

Comportamento especial:
    - Criação (POST): usa MovimentacaoCreateSerializer + Service
    - Leitura (GET): usa MovimentacaoSerializer com dados completos
    - Edição (PUT/PATCH): BLOQUEADA
    - Exclusão (DELETE): BLOQUEADA
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.movimentacoes.services import EstoqueService

from .models import Movimentacao
from .serializers import (
    MovimentacaoSerializer,
    MovimentacaoCreateSerializer,
    MovimentacaoDetalheSerializer,
)


class MovimentacaoViewSet(
    mixins.CreateModelMixin,    # POST /movimentacoes/
    mixins.RetrieveModelMixin,  # GET  /movimentacoes/{id}/
    mixins.ListModelMixin,      # GET  /movimentacoes/
    viewsets.GenericViewSet,    # Base sem nenhuma action padrão
):
    """
    ViewSet de Movimentacao — apenas criação e leitura.

    Por que não ModelViewSet?
    ModelViewSet incluiria PUT, PATCH e DELETE, que são proibidos.
    Usando mixins individuais, incluímos APENAS o que queremos.
    Isso segue o Princípio da Segregação de Interface (ISP do SOLID).

    Filtros:
        ?tipo=entrada
        ?tipo=saida
        ?produto=1
        ?search=notebook
        ?ordering=-data
    """

    queryset = Movimentacao.objects.select_related(
        "produto", "usuario"
    ).all()
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["tipo", "produto", "usuario"]
    search_fields = ["produto__nome", "observacao", "usuario__username"]
    ordering_fields = ["data", "quantidade", "tipo"]
    ordering = ["-data"]   # Mais recentes primeiro

    def get_serializer_class(self):
        """
        POST → MovimentacaoCreateSerializer (para criar)
        GET  → MovimentacaoDetalheSerializer (para ler com detalhes)
        """
        if self.action == "create":
            return MovimentacaoCreateSerializer
        if self.action == "retrieve":
            return MovimentacaoDetalheSerializer
        return MovimentacaoSerializer

    @action(detail=False, methods=["get"], url_path="dashboard")
    def dashboard(self, request: Request) -> Response:
        """
        Retorna estatísticas para o dashboard.
        GET /api/v1/movimentacoes/dashboard/

        Centraliza todos os dados que o dashboard precisa em uma única
        requisição, evitando múltiplas chamadas do frontend.
        """
        from django.utils import timezone
        from django.db.models import Sum, Count, Q

        hoje = timezone.now().date()
        service = EstoqueService()

        # Movimentações de hoje
        movimentacoes_hoje = Movimentacao.objects.filter(
            data__date=hoje
        )
        entradas_hoje = movimentacoes_hoje.filter(
            tipo=Movimentacao.TipoMovimentacao.ENTRADA
        ).aggregate(total=Sum("quantidade"))["total"] or 0

        saidas_hoje = movimentacoes_hoje.filter(
            tipo=Movimentacao.TipoMovimentacao.SAIDA
        ).aggregate(total=Sum("quantidade"))["total"] or 0

        # Últimas movimentações
        ultimas = service.ultimas_movimentacoes(limite=5)
        ultimas_serialized = MovimentacaoSerializer(
            ultimas, many=True, context={"request": request}
        ).data

        return Response({
            "total_produtos": service.total_produtos_ativos(),
            "produtos_abaixo_minimo": service.produtos_abaixo_do_minimo().count(),
            "produtos_sem_estoque": service.produtos_sem_estoque().count(),
            "entradas_hoje": entradas_hoje,
            "saidas_hoje": saidas_hoje,
            "ultimas_movimentacoes": ultimas_serialized,
        })
