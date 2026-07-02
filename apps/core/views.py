"""
views.py — View do Dashboard principal.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from apps.movimentacoes.models import Movimentacao
from apps.movimentacoes.services import EstoqueService


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = EstoqueService()

        from django.utils import timezone
        from django.db.models import Sum, Count
        from apps.movimentacoes.models import Movimentacao

        hoje = timezone.now().date()
        movs_hoje = Movimentacao.objects.filter(data__date=hoje)

        context.update({
            "total_produtos": service.total_produtos_ativos(),
            "produtos_criticos": service.produtos_abaixo_do_minimo().count(),
            "produtos_sem_estoque": service.produtos_sem_estoque().count(),
            "entradas_hoje": movs_hoje.filter(tipo="entrada").aggregate(
                t=Sum("quantidade"))["t"] or 0,
            "saidas_hoje": movs_hoje.filter(tipo="saida").aggregate(
                t=Sum("quantidade"))["t"] or 0,
            "ultimas_movimentacoes": service.ultimas_movimentacoes(limite=8),
            "produtos_criticos_lista": service.produtos_abaixo_do_minimo()[:5],
        })
        return context
