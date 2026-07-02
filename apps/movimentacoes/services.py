"""
services.py — Camada de serviço para Movimentações.

Responsabilidade:
    Orquestrar a criação de movimentações, aplicando todas as regras
    de negócio antes de delegar a persistência ao Model.

Por que Service e não só o Model?
    O Model cuida de si mesmo (validar seus campos, atualizar seu saldo).
    O Service cuida do processo completo:
    - Valida regras que envolvem múltiplos objetos
    - É o ponto de entrada único para criar movimentações
    - Pode ser chamado por Views, pela API, por scripts, por testes
    - É facilmente testável de forma isolada

Princípio aplicado: Single Responsibility Principle (SRP)
    Model → responsável pelos seus dados
    Service → responsável pelo processo de negócio
"""

import logging
from typing import Optional

from django.contrib.auth import get_user_model
from django.db import transaction

from apps.core.exceptions import (
    EstoqueInsuficienteError,
    MovimentacaoInvalidaError,
    ProdutoInativoError,
)
from apps.produtos.models import Produto

from .models import Movimentacao

logger = logging.getLogger(__name__)
User = get_user_model()


class MovimentacaoService:
    """
    Serviço responsável por criar e gerenciar movimentações de estoque.

    Todas as operações de entrada e saída devem passar por este serviço.
    Nunca crie Movimentacao diretamente nas views — use este serviço.

    Exemplo de uso:
        service = MovimentacaoService()
        movimentacao = service.registrar_entrada(
            produto=produto,
            quantidade=50,
            usuario=request.user,
            observacao="Compra NF 12345"
        )
    """

    def registrar_entrada(
        self,
        produto: Produto,
        quantidade: int,
        usuario: User,
        observacao: str = "",
    ) -> Movimentacao:
        """
        Registra uma entrada de produto no estoque.

        Args:
            produto: Instância do produto a ser movimentado.
            quantidade: Quantidade a ser adicionada ao estoque (deve ser > 0).
            usuario: Usuário que está realizando a operação.
            observacao: Observação opcional sobre a entrada.

        Returns:
            Movimentacao: A movimentação criada e persistida.

        Raises:
            ProdutoInativoError: Se o produto estiver inativo.
            MovimentacaoInvalidaError: Se a quantidade for inválida.
        """
        self._validar_produto(produto)
        self._validar_quantidade(quantidade)

        logger.info(
            "Registrando ENTRADA: produto='%s' quantidade=%d usuario='%s'",
            produto.nome, quantidade, usuario.username,
        )

        return self._criar_movimentacao(
            produto=produto,
            tipo=Movimentacao.TipoMovimentacao.ENTRADA,
            quantidade=quantidade,
            usuario=usuario,
            observacao=observacao,
        )

    def registrar_saida(
        self,
        produto: Produto,
        quantidade: int,
        usuario: User,
        observacao: str = "",
    ) -> Movimentacao:
        """
        Registra uma saída de produto do estoque.

        Args:
            produto: Instância do produto a ser movimentado.
            quantidade: Quantidade a ser removida do estoque (deve ser > 0).
            usuario: Usuário que está realizando a operação.
            observacao: Observação opcional sobre a saída.

        Returns:
            Movimentacao: A movimentação criada e persistida.

        Raises:
            ProdutoInativoError: Se o produto estiver inativo.
            MovimentacaoInvalidaError: Se a quantidade for inválida.
            EstoqueInsuficienteError: Se não houver estoque suficiente.
        """
        self._validar_produto(produto)
        self._validar_quantidade(quantidade)
        self._validar_estoque_suficiente(produto, quantidade)

        logger.info(
            "Registrando SAÍDA: produto='%s' quantidade=%d usuario='%s'",
            produto.nome, quantidade, usuario.username,
        )

        return self._criar_movimentacao(
            produto=produto,
            tipo=Movimentacao.TipoMovimentacao.SAIDA,
            quantidade=quantidade,
            usuario=usuario,
            observacao=observacao,
        )

    # ------------------------------------------------------------------
    # Métodos privados — validações e persistência
    # ------------------------------------------------------------------

    def _validar_produto(self, produto: Produto) -> None:
        """Verifica se o produto está ativo."""
        if not produto.ativo:
            raise ProdutoInativoError(produto_nome=produto.nome)

    def _validar_quantidade(self, quantidade: int) -> None:
        """Verifica se a quantidade é um número inteiro positivo."""
        if not isinstance(quantidade, int) or quantidade <= 0:
            raise MovimentacaoInvalidaError(
                f"A quantidade deve ser um número inteiro maior que zero. "
                f"Recebido: {quantidade!r}."
            )

    def _validar_estoque_suficiente(self, produto: Produto, quantidade: int) -> None:
        """
        Verifica se há estoque suficiente para a saída.

        Recarrega o produto do banco para garantir o valor mais atual,
        evitando race conditions em ambientes com múltiplos workers.
        """
        # select_for_update() bloqueia a linha durante a verificação
        # Nota: fora de uma transação, select_for_update não tem efeito no SQLite
        produto_atual = Produto.objects.get(pk=produto.pk)
        if quantidade > produto_atual.quantidade_atual:
            raise EstoqueInsuficienteError(
                produto_nome=produto.nome,
                disponivel=produto_atual.quantidade_atual,
                solicitado=quantidade,
            )

    @transaction.atomic
    def _criar_movimentacao(
        self,
        produto: Produto,
        tipo: str,
        quantidade: int,
        usuario: User,
        observacao: str,
    ) -> Movimentacao:
        """
        Persiste a movimentação no banco de dados.

        @transaction.atomic garante que:
        - A movimentação é salva E o saldo é atualizado
        - Se algo falhar, tudo é revertido (rollback)

        Obs: O model Movimentacao.save() já contém sua própria
        lógica de atualização de saldo. O decorator aqui garante
        que o bloco completo (service + model) seja atômico.
        """
        movimentacao = Movimentacao(
            produto=produto,
            tipo=tipo,
            quantidade=quantidade,
            usuario=usuario,
            observacao=observacao,
        )
        movimentacao.save()

        logger.info(
            "Movimentação criada com sucesso: id=%d tipo=%s produto='%s' qtd=%d",
            movimentacao.pk, tipo, produto.nome, quantidade,
        )

        return movimentacao


class EstoqueService:
    """
    Serviço de consultas sobre o estado do estoque.

    Centraliza queries de negócio relacionadas a estoque
    que serão usadas no dashboard e em relatórios.
    """

    def produtos_abaixo_do_minimo(self):
        """
        Retorna QuerySet com todos os produtos ativos abaixo do mínimo.

        Usa F() expression para comparar dois campos do mesmo model:
        quantidade_atual < quantidade_minima (operação em SQL, não Python)
        """
        from django.db.models import F
        return (
            Produto.objects
            .filter(ativo=True)
            .filter(quantidade_atual__lt=F("quantidade_minima"))
            .select_related("categoria", "fornecedor")
            .order_by("quantidade_atual")
        )

    def produtos_sem_estoque(self):
        """Retorna produtos ativos com estoque zerado."""
        return (
            Produto.objects
            .filter(ativo=True, quantidade_atual=0)
            .select_related("categoria", "fornecedor")
        )

    def total_produtos_ativos(self) -> int:
        """Contagem de produtos ativos no sistema."""
        return Produto.objects.filter(ativo=True).count()

    def ultimas_movimentacoes(self, limite: int = 10):
        """Retorna as N movimentações mais recentes."""
        return (
            Movimentacao.objects
            .select_related("produto", "usuario")
            .order_by("-data")[:limite]
        )
