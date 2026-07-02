"""
models.py — Model de Produto.

Produto é a entidade central do sistema.
Relaciona-se com Categoria e Fornecedor (N:1).
Possui métodos de negócio que serão expandidos na Etapa 3.

Design decisions:
- quantidade_atual começa em 0: nenhum produto entra com saldo arbitrário.
  O saldo é sempre construído via Movimentacoes (rastreabilidade).
- preco usa DecimalField (não FloatField): FloatField tem imprecisão em
  operações monetárias (ex: 0.1 + 0.2 != 0.3). DecimalField é exato.
- on_delete=PROTECT nas FKs: impede excluir categoria/fornecedor que
  tem produtos vinculados, evitando dados órfãos.
"""

from django.db import models


class Produto(models.Model):
    """
    Representa um produto controlado pelo sistema de estoque.

    Atributos:
        nome: Nome do produto.
        categoria: Categoria à qual o produto pertence (FK).
        fornecedor: Fornecedor do produto (FK).
        preco: Preço unitário do produto.
        quantidade_atual: Saldo atual em estoque (atualizado por Movimentacao).
        quantidade_minima: Estoque mínimo — abaixo disso emite alerta.
        ativo: Permite desativar sem excluir.
        criado_em / atualizado_em: Auditoria automática.
    """

    nome = models.CharField(
        max_length=200,
        verbose_name="Nome",
        help_text="Nome do produto.",
    )
    categoria = models.ForeignKey(
        # String 'apps.categorias.Categoria' evita import circular.
        # O Django resolve a referência em tempo de execução.
        "categorias.Categoria",
        on_delete=models.PROTECT,   # Protege: não deixa excluir categoria com produtos
        related_name="produtos",    # categoria.produtos.all() → todos os produtos da categoria
        verbose_name="Categoria",
    )
    fornecedor = models.ForeignKey(
        "fornecedores.Fornecedor",
        on_delete=models.PROTECT,
        related_name="produtos",
        verbose_name="Fornecedor",
    )
    preco = models.DecimalField(
        max_digits=10,       # Total de dígitos
        decimal_places=2,    # Dígitos após a vírgula: R$ 99999999.99
        verbose_name="Preço (R$)",
    )
    quantidade_atual = models.IntegerField(
        default=0,
        verbose_name="Quantidade Atual",
        help_text="Saldo atual em estoque. Atualizado automaticamente pelas movimentações.",
    )
    quantidade_minima = models.IntegerField(
        default=0,
        verbose_name="Quantidade Mínima",
        help_text="Quantidade mínima em estoque. Abaixo disso o sistema emitirá alerta.",
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Desmarque para desativar o produto sem excluí-lo.",
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    class Meta:
        db_table = "produtos_produto"
        ordering = ["nome"]
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"

    def __str__(self) -> str:
        return self.nome

    # ------------------------------------------------------------------
    # Métodos de negócio
    # Colocamos a lógica no Model (Fat Model) em vez da View (Thin View).
    # Princípio: quem conhece os dados é responsável pelas regras sobre eles.
    # ------------------------------------------------------------------

    def esta_abaixo_do_minimo(self) -> bool:
        """
        Verifica se o produto está com estoque abaixo do mínimo.

        Retorna True se quantidade_atual < quantidade_minima.
        Usado para exibir alertas visuais no dashboard e na listagem.

        Exemplo:
            produto.quantidade_atual = 5
            produto.quantidade_minima = 10
            produto.esta_abaixo_do_minimo()  # → True
        """
        return self.quantidade_atual < self.quantidade_minima

    def esta_sem_estoque(self) -> bool:
        """
        Verifica se o produto está completamente sem estoque.

        Retorna True se quantidade_atual == 0.
        """
        return self.quantidade_atual == 0

    @property
    def status_estoque(self) -> str:
        """
        Retorna o status textual do estoque para exibição na interface.

        Retornos possíveis:
            'sem_estoque'   → quantidade = 0
            'abaixo_minimo' → quantidade > 0 mas < mínimo
            'normal'        → quantidade >= mínimo
        """
        if self.esta_sem_estoque():
            return "sem_estoque"
        if self.esta_abaixo_do_minimo():
            return "abaixo_minimo"
        return "normal"

    @property
    def valor_total_estoque(self) -> float:
        """
        Calcula o valor total do produto em estoque.

        Fórmula: quantidade_atual × preço
        Útil para relatórios financeiros.
        """
        return self.quantidade_atual * self.preco
