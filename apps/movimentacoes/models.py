"""
models.py — Model de Movimentação.

Movimentação é o registro de entrada ou saída de produtos do estoque.
É a entidade mais importante do sistema do ponto de vista de negócio.

Regras de negócio implementadas aqui:
1. Uma SAÍDA nunca pode gerar estoque negativo → ValidationError
2. O saldo do produto é atualizado automaticamente no save()
3. Movimentações não podem ser editadas após criadas (auditoria)
   → somente criação, nunca alteração

Design decisions:
- on_delete=PROTECT no produto: não permite excluir produto com movimentações.
  Isso preserva o histórico completo do estoque.
- Usamos django.db.transaction.atomic() para garantir que a atualização
  do saldo e o registro da movimentação aconteçam juntos ou nenhum deles.
  (Atomicidade — o 'A' do ACID)
- O campo 'usuario' usa settings.AUTH_USER_MODEL em vez de importar User
  diretamente. Isso respeita o modelo de usuário customizado (Etapa 4).
"""

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction


class Movimentacao(models.Model):
    """
    Registra uma entrada ou saída de produto no estoque.

    Atributos:
        produto: Produto movimentado (FK).
        tipo: 'entrada' ou 'saida'.
        quantidade: Quantidade movimentada (sempre positiva).
        usuario: Usuário que registrou a movimentação (FK).
        observacao: Observação opcional.
        data: Data/hora da movimentação (preenchida automaticamente).
    """

    class TipoMovimentacao(models.TextChoices):
        """
        Enum de tipos de movimentação.

        TextChoices cria constantes legíveis:
            Movimentacao.TipoMovimentacao.ENTRADA → 'entrada'
            Movimentacao.TipoMovimentacao.SAIDA   → 'saida'

        Vantagem sobre strings literais: evita typos e permite autocomplete.
        """
        ENTRADA = "entrada", "Entrada"
        SAIDA = "saida", "Saída"

    produto = models.ForeignKey(
        "produtos.Produto",
        on_delete=models.PROTECT,       # Não permite excluir produto com movimentações
        related_name="movimentacoes",   # produto.movimentacoes.all()
        verbose_name="Produto",
    )
    tipo = models.CharField(
        max_length=10,
        choices=TipoMovimentacao.choices,
        verbose_name="Tipo",
        help_text="Entrada aumenta o estoque. Saída diminui o estoque.",
    )
    quantidade = models.PositiveIntegerField(
        verbose_name="Quantidade",
        help_text="Quantidade movimentada. Deve ser maior que zero.",
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,       # Usa o modelo de usuário do projeto (flexível)
        on_delete=models.PROTECT,
        related_name="movimentacoes",
        verbose_name="Usuário",
    )
    observacao = models.TextField(
        blank=True,
        default="",
        verbose_name="Observação",
        help_text="Observação opcional sobre a movimentação.",
    )
    data = models.DateTimeField(
        auto_now_add=True,              # Preenchida automaticamente na criação
        verbose_name="Data",
    )

    class Meta:
        db_table = "movimentacoes_movimentacao"
        ordering = ["-data"]            # Mais recentes primeiro
        verbose_name = "Movimentação"
        verbose_name_plural = "Movimentações"

    def __str__(self) -> str:
        return (
            f"{self.get_tipo_display()} de {self.quantidade}x "
            f"{self.produto.nome} em {self.data.strftime('%d/%m/%Y %H:%M')}"
        )

    # ------------------------------------------------------------------
    # Validação — clean() é chamado antes de save() em formulários e pela API
    # ------------------------------------------------------------------

    def clean(self) -> None:
        """
        Valida as regras de negócio antes de salvar.

        clean() é o local correto para validações de negócio no Django.
        É chamado automaticamente por ModelForm e pela API (via serializer).

        Regras validadas:
        1. Quantidade deve ser maior que zero
        2. Uma saída não pode gerar estoque negativo
        """
        super().clean()

        # Regra 1: quantidade deve ser positiva
        if self.quantidade is not None and self.quantidade <= 0:
            raise ValidationError({
                "quantidade": "A quantidade deve ser maior que zero."
            })

        # Regra 2: saída não pode gerar estoque negativo
        if self.tipo == self.TipoMovimentacao.SAIDA and self.produto_id:
            # Recarrega o produto do banco para ter o valor mais atual
            # (evita race conditions em ambientes com múltiplos workers)
            try:
                produto_atual = self.produto.__class__.objects.get(pk=self.produto_id)
                if self.quantidade > produto_atual.quantidade_atual:
                    raise ValidationError({
                        "quantidade": (
                            f"Estoque insuficiente. "
                            f"Disponível: {produto_atual.quantidade_atual} unidade(s). "
                            f"Solicitado: {self.quantidade} unidade(s)."
                        )
                    })
            except self.produto.__class__.DoesNotExist:
                pass

    # ------------------------------------------------------------------
    # save() — persiste e atualiza o saldo automaticamente
    # ------------------------------------------------------------------

    def save(self, *args, **kwargs) -> None:
        """
        Sobrescreve o save() para:
        1. Executar as validações (full_clean → clean)
        2. Atualizar o saldo do produto atomicamente

        transaction.atomic() garante que:
        - A movimentação é salva E o saldo é atualizado
        - Se qualquer um falhar, AMBOS são desfeitos (rollback)
        - Sem risco de saldo inconsistente no banco

        Conceito ACID:
        A = Atomicidade  → tudo ou nada
        C = Consistência → dados sempre válidos
        I = Isolamento   → transações não interferem entre si
        D = Durabilidade → dados persistem após commit
        """
        # Só permite criar movimentações, nunca editar
        # (self.pk é None quando o objeto ainda não foi salvo)
        if self.pk is not None:
            raise ValidationError(
                "Movimentações não podem ser editadas após criadas. "
                "Registre uma nova movimentação para corrigir."
            )

        # Executa as validações de negócio
        self.full_clean()

        # Bloco atômico: movimentação + atualização de saldo são uma unidade
        with transaction.atomic():
            super().save(*args, **kwargs)
            self._atualizar_saldo_produto()

    def _atualizar_saldo_produto(self) -> None:
        """
        Atualiza o saldo do produto após a movimentação.

        Usamos F() expression em vez de:
            produto.quantidade_atual += self.quantidade  ← ERRADO (race condition)

        F() expression faz a operação diretamente no SQL:
            UPDATE produtos SET quantidade_atual = quantidade_atual + X
        Isso é seguro em ambientes com múltiplos workers simultâneos.

        Método privado (prefixo _): não deve ser chamado externamente.
        É responsabilidade exclusiva deste model.
        """
        from django.db.models import F

        produto = self.produto.__class__.objects.select_for_update().get(
            pk=self.produto_id
        )

        if self.tipo == self.TipoMovimentacao.ENTRADA:
            produto.__class__.objects.filter(pk=self.produto_id).update(
                quantidade_atual=F("quantidade_atual") + self.quantidade
            )
        else:  # SAIDA
            produto.__class__.objects.filter(pk=self.produto_id).update(
                quantidade_atual=F("quantidade_atual") - self.quantidade
            )
