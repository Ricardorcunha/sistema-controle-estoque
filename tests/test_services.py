"""
test_services.py — Testes da camada de Services.

Aqui testamos o MovimentacaoService e o EstoqueService.
Esses testes verificam se o Service lança as exceções corretas
e se orquestra os models adequadamente.
"""

import pytest

from apps.core.exceptions import (
    EstoqueInsuficienteError,
    MovimentacaoInvalidaError,
    ProdutoInativoError,
)
from apps.movimentacoes.models import Movimentacao
from apps.movimentacoes.services import EstoqueService, MovimentacaoService

from .factories import ProdutoFactory, UserFactory


# ===========================================================================
# TESTES — MovimentacaoService
# ===========================================================================

@pytest.mark.django_db
class TestMovimentacaoService:
    """Testes para o MovimentacaoService."""

    def setup_method(self):
        """
        setup_method é chamado antes de cada método de teste.
        Aqui instanciamos o service e criamos dados comuns.
        """
        self.service = MovimentacaoService()
        self.usuario = UserFactory()
        self.produto = ProdutoFactory(quantidade_atual=100, quantidade_minima=10)

    # --- registrar_entrada ---

    def test_registrar_entrada_com_sucesso(self):
        """Deve criar movimentação de entrada e atualizar saldo."""
        movimentacao = self.service.registrar_entrada(
            produto=self.produto,
            quantidade=50,
            usuario=self.usuario,
            observacao="Compra NF 001",
        )

        assert movimentacao.pk is not None
        assert movimentacao.tipo == Movimentacao.TipoMovimentacao.ENTRADA
        assert movimentacao.quantidade == 50
        assert movimentacao.observacao == "Compra NF 001"

        self.produto.refresh_from_db()
        assert self.produto.quantidade_atual == 150

    def test_registrar_entrada_produto_inativo_levanta_erro(self):
        """Não deve permitir movimentação em produto inativo."""
        produto_inativo = ProdutoFactory(ativo=False)

        with pytest.raises(ProdutoInativoError) as exc_info:
            self.service.registrar_entrada(
                produto=produto_inativo,
                quantidade=10,
                usuario=self.usuario,
            )

        assert produto_inativo.nome in str(exc_info.value)

    def test_registrar_entrada_quantidade_zero_levanta_erro(self):
        """Quantidade zero deve lançar MovimentacaoInvalidaError."""
        with pytest.raises(MovimentacaoInvalidaError):
            self.service.registrar_entrada(
                produto=self.produto,
                quantidade=0,
                usuario=self.usuario,
            )

    def test_registrar_entrada_quantidade_negativa_levanta_erro(self):
        """Quantidade negativa deve lançar MovimentacaoInvalidaError."""
        with pytest.raises(MovimentacaoInvalidaError):
            self.service.registrar_entrada(
                produto=self.produto,
                quantidade=-5,
                usuario=self.usuario,
            )

    # --- registrar_saida ---

    def test_registrar_saida_com_sucesso(self):
        """Deve criar movimentação de saída e diminuir saldo."""
        movimentacao = self.service.registrar_saida(
            produto=self.produto,
            quantidade=30,
            usuario=self.usuario,
        )

        assert movimentacao.pk is not None
        assert movimentacao.tipo == Movimentacao.TipoMovimentacao.SAIDA

        self.produto.refresh_from_db()
        assert self.produto.quantidade_atual == 70

    def test_registrar_saida_estoque_insuficiente_levanta_erro(self):
        """
        REGRA CRÍTICA: Saída maior que estoque disponível deve falhar.
        Verifica: exceção correta, mensagem informativa, saldo inalterado.
        """
        produto = ProdutoFactory(quantidade_atual=5)

        with pytest.raises(EstoqueInsuficienteError) as exc_info:
            self.service.registrar_saida(
                produto=produto,
                quantidade=10,
                usuario=self.usuario,
            )

        erro = exc_info.value
        assert erro.disponivel == 5
        assert erro.solicitado == 10
        assert produto.nome in str(erro)

        # Saldo deve permanecer inalterado
        produto.refresh_from_db()
        assert produto.quantidade_atual == 5

    def test_registrar_saida_produto_inativo_levanta_erro(self):
        """Não deve processar saída de produto inativo."""
        produto_inativo = ProdutoFactory(ativo=False, quantidade_atual=100)

        with pytest.raises(ProdutoInativoError):
            self.service.registrar_saida(
                produto=produto_inativo,
                quantidade=10,
                usuario=self.usuario,
            )

    def test_saida_com_estoque_exato_funciona(self):
        """Saída igual ao estoque disponível deve ser permitida."""
        produto = ProdutoFactory(quantidade_atual=10)

        movimentacao = self.service.registrar_saida(
            produto=produto,
            quantidade=10,
            usuario=self.usuario,
        )

        assert movimentacao.pk is not None
        produto.refresh_from_db()
        assert produto.quantidade_atual == 0


# ===========================================================================
# TESTES — EstoqueService
# ===========================================================================

@pytest.mark.django_db
class TestEstoqueService:
    """Testes para o EstoqueService."""

    def setup_method(self):
        self.service = EstoqueService()

    def test_produtos_abaixo_do_minimo(self):
        """Deve retornar apenas produtos com estoque abaixo do mínimo."""
        # Produtos abaixo do mínimo
        p1 = ProdutoFactory(quantidade_atual=2, quantidade_minima=10, ativo=True)
        p2 = ProdutoFactory(quantidade_atual=5, quantidade_minima=20, ativo=True)
        # Produto normal
        ProdutoFactory(quantidade_atual=50, quantidade_minima=10, ativo=True)
        # Produto inativo (não deve aparecer)
        ProdutoFactory(quantidade_atual=2, quantidade_minima=10, ativo=False)

        resultado = self.service.produtos_abaixo_do_minimo()

        pks = list(resultado.values_list("pk", flat=True))
        assert p1.pk in pks
        assert p2.pk in pks
        assert len(pks) == 2

    def test_produtos_sem_estoque(self):
        """Deve retornar produtos ativos com estoque zero."""
        sem_estoque = ProdutoFactory(quantidade_atual=0, ativo=True)
        ProdutoFactory(quantidade_atual=10, ativo=True)
        ProdutoFactory(quantidade_atual=0, ativo=False)  # inativo, não conta

        resultado = self.service.produtos_sem_estoque()

        pks = list(resultado.values_list("pk", flat=True))
        assert sem_estoque.pk in pks
        assert len(pks) == 1

    def test_total_produtos_ativos(self):
        """Deve contar apenas produtos ativos."""
        ProdutoFactory.create_batch(3, ativo=True)
        ProdutoFactory.create_batch(2, ativo=False)

        assert self.service.total_produtos_ativos() == 3

    def test_ultimas_movimentacoes(self):
        """Deve retornar as N movimentações mais recentes."""
        usuario = UserFactory()
        produto = ProdutoFactory(quantidade_atual=1000)

        for i in range(5):
            Movimentacao.objects.create(
                produto=produto,
                tipo="entrada",
                quantidade=1,
                usuario=usuario,
            )

        resultado = self.service.ultimas_movimentacoes(limite=3)
        assert len(list(resultado)) == 3

    def test_ultimas_movimentacoes_sem_dados(self):
        """Com banco vazio, deve retornar lista vazia."""
        resultado = self.service.ultimas_movimentacoes()
        assert len(list(resultado)) == 0
