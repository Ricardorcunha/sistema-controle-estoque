"""
admin.py — Configuração do Django Admin para Fornecedor.
"""

from django.contrib import admin

from .models import Fornecedor


@admin.register(Fornecedor)
class FornecedorAdmin(admin.ModelAdmin):
    """Admin customizado para o model Fornecedor."""

    list_display = ["nome", "cnpj", "email", "telefone", "ativo", "total_produtos"]
    list_filter = ["ativo"]          # Filtro lateral por status ativo/inativo
    search_fields = ["nome", "cnpj", "email"]
    readonly_fields = ["criado_em", "atualizado_em"]

    # Permite ativar/desativar diretamente na listagem
    list_editable = ["ativo"]

    fieldsets = [
        ("Informações", {
            "fields": ["nome", "cnpj", "ativo"],
        }),
        ("Contato", {
            "fields": ["email", "telefone"],
        }),
        ("Auditoria", {
            "fields": ["criado_em", "atualizado_em"],
            "classes": ["collapse"],
        }),
    ]

    @admin.display(description="Nº de Produtos")
    def total_produtos(self, obj: Fornecedor) -> int:
        """Exibe quantos produtos este fornecedor possui."""
        return obj.produtos.count()
