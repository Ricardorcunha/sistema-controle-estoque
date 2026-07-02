"""
admin.py — Configuração do Django Admin para Categoria.

O Admin do Django é uma ferramenta poderosa para gerenciar dados.
Customizamos para torná-lo mais produtivo e informativo.
"""

from django.contrib import admin

from .models import Categoria


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """Admin customizado para o model Categoria."""

    # Colunas exibidas na listagem
    list_display = ["nome", "descricao_curta", "total_produtos", "criado_em"]

    # Campos pelo quais é possível buscar (barra de pesquisa)
    search_fields = ["nome", "descricao"]

    # Campos somente leitura (não editáveis no admin)
    readonly_fields = ["criado_em", "atualizado_em"]

    # Organização dos campos no formulário de edição
    fieldsets = [
        ("Informações", {
            "fields": ["nome", "descricao"],
        }),
        ("Auditoria", {
            "fields": ["criado_em", "atualizado_em"],
            "classes": ["collapse"],  # Seção colapsável
        }),
    ]

    @admin.display(description="Descrição")
    def descricao_curta(self, obj: Categoria) -> str:
        """Exibe os primeiros 50 caracteres da descrição na listagem."""
        if obj.descricao:
            return obj.descricao[:50] + ("..." if len(obj.descricao) > 50 else "")
        return "—"

    @admin.display(description="Nº de Produtos")
    def total_produtos(self, obj: Categoria) -> int:
        """Exibe quantos produtos pertencem a esta categoria."""
        return obj.produtos.count()
