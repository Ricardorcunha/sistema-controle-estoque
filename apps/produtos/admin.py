"""
admin.py — Configuração do Django Admin para Produto.
"""

from django.contrib import admin
from django.utils.html import format_html

from .models import Produto


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """Admin customizado para o model Produto."""

    list_display = [
        "nome", "categoria", "fornecedor",
        "preco", "quantidade_atual", "quantidade_minima",
        "badge_status", "ativo",
    ]
    list_filter = ["ativo", "categoria", "fornecedor"]
    search_fields = ["nome", "categoria__nome", "fornecedor__nome"]
    readonly_fields = ["quantidade_atual", "criado_em", "atualizado_em"]
    list_editable = ["ativo"]

    fieldsets = [
        ("Informações do Produto", {
            "fields": ["nome", "categoria", "fornecedor", "ativo"],
        }),
        ("Preço e Estoque", {
            "fields": ["preco", "quantidade_atual", "quantidade_minima"],
        }),
        ("Auditoria", {
            "fields": ["criado_em", "atualizado_em"],
            "classes": ["collapse"],
        }),
    ]

    @admin.display(description="Status", ordering="quantidade_atual")
    def badge_status(self, obj: Produto) -> str:
        """
        Exibe um badge colorido com o status do estoque.

        format_html() é obrigatório ao retornar HTML no admin.
        Ele protege contra XSS (Cross-Site Scripting).
        """
        status = obj.status_estoque
        cores = {
            "sem_estoque": ("#dc3545", "Sem Estoque"),
            "abaixo_minimo": ("#fd7e14", "Abaixo do Mínimo"),
            "normal": ("#198754", "Normal"),
        }
        cor, label = cores[status]
        return format_html(
            '<span style="'
            'background-color: {}; color: white; '
            'padding: 2px 8px; border-radius: 4px; '
            'font-size: 11px; font-weight: bold;">'
            '{}</span>',
            cor, label,
        )
