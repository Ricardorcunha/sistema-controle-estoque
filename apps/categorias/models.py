"""
models.py — Model de Categoria.

Categoria é a forma de agrupar produtos por tipo.
Ex: Eletrônicos, Alimentos, Ferramentas, Papelaria.

Design decision: model simples e direto.
Não há necessidade de hierarquia (categoria pai/filho) neste escopo.
Se o projeto crescer, podemos adicionar um campo 'parent' (FK para si mesmo).
"""

from django.db import models


class Categoria(models.Model):
    """
    Representa uma categoria de produtos no estoque.

    Atributos:
        nome: Nome único da categoria.
        descricao: Descrição opcional da categoria.
        criado_em: Data/hora de criação (preenchida automaticamente).
        atualizado_em: Data/hora da última atualização (atualizada automaticamente).
    """

    nome = models.CharField(
        max_length=100,
        unique=True,          # Não permite duas categorias com o mesmo nome
        verbose_name="Nome",
        help_text="Nome da categoria (deve ser único).",
    )
    descricao = models.TextField(
        blank=True,           # Campo opcional no formulário
        default="",
        verbose_name="Descrição",
        help_text="Descrição opcional da categoria.",
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,    # Preenchido automaticamente na criação
        verbose_name="Criado em",
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,        # Atualizado automaticamente a cada save()
        verbose_name="Atualizado em",
    )

    class Meta:
        # Nome das tabelas no banco: categorias_categoria
        db_table = "categorias_categoria"
        # Ordenação padrão ao listar categorias
        ordering = ["nome"]
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"

    def __str__(self) -> str:
        """
        Representação em string do objeto.
        Usada no Admin, em ForeignKey dropdowns e no shell.
        """
        return self.nome
