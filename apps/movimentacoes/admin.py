"""
admin.py — Configuração do Django Admin para Movimentação.

Movimentações são somente leitura no admin após criadas.
A única operação permitida é CRIAR — nunca editar ou excluir.
Isso garante a integridade do histórico do estoque.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Movimentacao


@admin.register(Movimentacao)
class MovimentacaoAdmin(admin.ModelAdmin):
    """Admin customizado para o model Movimentacao."""

    list_display = [
        "data", "produto", "badge_tipo",
        "quantidade", "usuario", "observacao_curta",
    ]
    list_filter = ["tipo", "data", "produto__categoria"]
    search_fields = ["produto__nome", "usuario__username", "observacao"]
    readonly_fields = ["produto", "tipo", "quantidade", "usuario", "data", "observacao"]
    date_hierarchy = "data"    # Navegação por data no topo da listagem

    # Remove as ações padrão de deletar (preservar histórico)
    actions = None

    def has_change_permission(self, request, obj=None) -> bool:
        """Desabilita edição de movimentações no admin."""
        return False

    def has_delete_permission(self, request, obj=None) -> bool:
        """Desabilita exclusão de movimentações no admin."""
        return False

    @admin.display(description="Tipo", ordering="tipo")
    def badge_tipo(self, obj: Movimentacao) -> str:
        """Exibe badge colorido para o tipo de movimentação."""
        if obj.tipo == Movimentacao.TipoMovimentacao.ENTRADA:
            cor, label = "#198754", "↑ Entrada"
        else:
            cor, label = "#dc3545", "↓ Saída"

        return format_html(
            '<span style="'
            'background-color: {}; color: white; '
            'padding: 2px 8px; border-radius: 4px; '
            'font-size: 11px; font-weight: bold;">'
            '{}</span>',
            cor, label,
        )

    @admin.display(description="Observação")
    def observacao_curta(self, obj: Movimentacao) -> str:
        """Exibe os primeiros 40 caracteres da observação."""
        if obj.observacao:
            return obj.observacao[:40] + ("..." if len(obj.observacao) > 40 else "")
        return "—"
