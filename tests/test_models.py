"""
test_models.py — Testes dos Models do sistema de estoque.

Convenção pytest:
- Arquivo começa com test_
- Classes começam com Test
- Métodos começam com test_

O decorator @pytest.mark.django_db permite acesso ao banco de dados.
Sem ele, qualquer acesso ao banco levanta um erro — isso é intencional
para forçar o uso explícito do decorator (testes são mais rápidos sem DB).

Estrutura de cada teste (padrão AAA):
    Arrange → prepara os dados
    Act     → executa a ação
    Assert  → verifica o resultado
"""

import pytest
from django.core.exceptions import ValidationError

from apps.categorias.models import Categoria
from apps.fornecedores.models import Fornecedor
from apps.produtos.models import Produto
from apps.movimentacoes.models import Movimentacao

from .factories import (
    CategoriaFactory,
    FornecedorFactory,
    ProdutoFactory,
    UserFactory,
)


# ===========================================================================
# TESTES — Categoria
# ===========================================================================

@pytest.mark.django_db
class TestCategoriaModel:
    """Testes para o model Categoria."""

    def test_criar_categoria(self):
        """Deve criar uma categoria com sucesso."""
        # Arrange + Act
        categoria = CategoriaFactory(nome="Eletrônicos")

        # Assert
        assert categoria.pk is not None
        assert categoria.nome == "Eletrônicos"
        assert Categoria.objects.count() == 1

    def test_str_retorna_nome(self):
        """__str__ deve retornar o nome da categoria."""
        categoria = CategoriaFactory(nome="Ferramentas")
        assert str(categoria) == "Ferramentas"

    def test_nome_unico(self):
        """Não deve permitir duas categorias com o mesmo nome."""
        CategoriaFactory(nome="Alimentos")

        with pytest.raises(Exception):  # IntegrityError ou ValidationError
            CategoriaFactory(nome="Alimentos")

    def test_ordenacao_por_nome(self):
        """Categorias devem ser ordenadas alfabeticamente."""
        CategoriaFactory(nome="Zzz")
        CategoriaFactory(nome="Aaa")
        CategoriaFactory(nome="Mmm")

        nomes = list(Categoria.objects.values_list("nome", flat=True))
        assert nomes == sorted(nomes)


# ===========================================================================
# TESTES — Fornecedor
# ===========================================================================

@pytest.mark.django_db
class TestFornecedorModel:
    """Testes para o model Fornecedor."""

    def test_criar_fornecedor(self):
        """Deve criar um fornecedor com sucesso."""
        fornecedor = FornecedorFactory(nome="Tech Supply Ltda")

        assert fornecedor.pk is not None
        assert fornecedor.nome == "Tech Supply Ltda"
        assert fornecedor.ativo is True

    def test_str_inclui_nome_e_cnpj(self):
        """__str__ deve incluir nome e CNPJ."""
        fornecedor = FornecedorFactory(nome="Empresa X", cnpj="12345678000195")

        resultado = str(fornecedor)
        assert "Empresa X" in resultado
        assert "12345678000195" in resultado

    def test_cnpj_formatado(self):
        """Propriedade cnpj_formatado deve retornar CNPJ com máscara."""
        fornecedor = FornecedorFactory(cnpj="11222333000181")

        assert fornecedor.cnpj_formatado == "11.222.333/0001-81"

    def test_cnpj_formatado_invalido_retorna_original(self):
        """CNPJ com número incorreto de dígitos retorna o valor original."""
        fornecedor = FornecedorFactory(cnpj="123")

        assert fornecedor.cnpj_formatado == "123"

    def test_fornecedor_inativo(self):
        """Deve criar fornecedor inativo corretamente."""
        fornecedor = FornecedorFactory(ativo=False)

        assert fornecedor.ativo is False


# ===========================================================================
# TESTES — Produto
# ===========================================================================

@pytest.mark.django_db
class TestProdutoModel:
    """Testes para o model Produto e seus métodos de negócio."""

    def test_criar_produto(self):
        """Deve criar um produto com sucesso."""
        produto = ProdutoFactory(nome="Notebook", quantidade_atual=50)

        assert produto.pk is not None
        assert produto.nome == "Notebook"
        assert produto.quantidade_atual == 50

    def test_str_retorna_nome(self):
        """__str__ deve retornar o nome do produto."""
        produto = ProdutoFactory(nome="Mouse Gamer")
        assert str(produto) == "Mouse Gamer"

    # --- esta_abaixo_do_minimo() ---

    def test_esta_abaixo_do_minimo_true(self):
        """Deve retornar True quando quantidade_atual < quantidade_minima."""
        produto = ProdutoFactory(quantidade_atual=5, quantidade_minima=10)
        assert produto.esta_abaixo_do_minimo() is True

    def test_esta_abaixo_do_minimo_false_quando_igual(self):
        """Deve retornar False quando quantidade_atual == quantidade_minima."""
        produto = ProdutoFactory(quantidade_atual=10, quantidade_minima=10)
        assert produto.esta_abaixo_do_minimo() is False

    def test_esta_abaixo_do_minimo_false_quando_acima(self):
        """Deve retornar False quando quantidade_atual > quantidade_minima."""
        produto = ProdutoFactory(quantidade_atual=20, quantidade_minima=10)
        assert produto.esta_abaixo_do_minimo() is False

    # --- esta_sem_estoque() ---

    def test_esta_sem_estoque_true(self):
        """Deve retornar True quando quantidade_atual == 0."""
        produto = ProdutoFactory(quantidade_atual=0)
        assert produto.esta_sem_estoque() is True

    def test_esta_sem_estoque_false(self):
        """Deve retornar False quando quantidade_atual > 0."""
        produto = ProdutoFactory(quantidade_atual=1)
        assert produto.esta_sem_estoque() is False

    # --- status_estoque ---

    def test_status_estoque_sem_estoque(self):
        produto = ProdutoFactory(quantidade_atual=0, quantidade_minima=10)
        assert produto.status_estoque == "sem_estoque"

    def test_status_estoque_abaixo_minimo(self):
        produto = ProdutoFactory(quantidade_atual=3, quantidade_minima=10)
        assert produto.status_estoque == "abaixo_minimo"

    def test_status_estoque_normal(self):
        produto = ProdutoFactory(quantidade_atual=50, quantidade_minima=10)
        assert produto.status_estoque == "normal"

    # --- valor_total_estoque ---

    def test_valor_total_estoque(self):
        """Deve calcular corretamente quantidade × preço."""
        from decimal import Decimal
        produto = ProdutoFactory(quantidade_atual=10, preco=Decimal("25.50"))
        assert produto.valor_total_estoque == Decimal("255.00")

    def test_valor_total_estoque_zerado(self):
        """Produto sem estoque tem valor total zero."""
        from decimal import Decimal
        produto = ProdutoFactory(quantidade_atual=0, preco=Decimal("100.00"))
        assert produto.valor_total_estoque == Decimal("0.00")


# ===========================================================================
# TESTES — Movimentacao (Model)
# ===========================================================================

@pytest.mark.django_db
class TestMovimentacaoModel:
    """
    Testes para o model Movimentacao.
    Foca nas regras de negócio: validações e atualização de saldo.
    """

    def test_entrada_aumenta_estoque(self):
        """
        REGRA: Uma entrada deve aumentar o quantidade_atual do produto.
        """
        # Arrange
        usuario = UserFactory()
        produto = ProdutoFactory(quantidade_atual=10)

        # Act
        Movimentacao.objects.create(
            produto=produto,
            tipo=Movimentacao.TipoMovimentacao.ENTRADA,
            quantidade=20,
            usuario=usuario,
        )

        # Assert — recarrega do banco para ver o valor atualizado
        produto.refresh_from_db()
        assert produto.quantidade_atual == 30

    def test_saida_diminui_estoque(self):
        """
        REGRA: Uma saída deve diminuir o quantidade_atual do produto.
        """
        usuario = UserFactory()
        produto = ProdutoFactory(quantidade_atual=50)

        Movimentacao.objects.create(
            produto=produto,
            tipo=Movimentacao.TipoMovimentacao.SAIDA,
            quantidade=15,
            usuario=usuario,
        )

        produto.refresh_from_db()
        assert produto.quantidade_atual == 35

    def test_saida_com_estoque_exato_zera_produto(self):
        """
        REGRA: Saída igual ao estoque disponível deve zerar o produto (não negativo).
        """
        usuario = UserFactory()
        produto = ProdutoFactory(quantidade_atual=10)

        Movimentacao.objects.create(
            produto=produto,
            tipo=Movimentacao.TipoMovimentacao.SAIDA,
            quantidade=10,
            usuario=usuario,
        )

        produto.refresh_from_db()
        assert produto.quantidade_atual == 0

    def test_saida_impede_estoque_negativo(self):
        """
        REGRA CRÍTICA: Uma saída NÃO pode gerar estoque negativo.
        Deve lançar ValidationError antes de salvar.
        """
        usuario = UserFactory()
        produto = ProdutoFactory(quantidade_atual=5)

        with pytest.raises(ValidationError) as exc_info:
            Movimentacao.objects.create(
                produto=produto,
                tipo=Movimentacao.TipoMovimentacao.SAIDA,
                quantidade=10,  # maior que o disponível (5)
                usuario=usuario,
            )

        # Verifica que o saldo NÃO foi alterado
        produto.refresh_from_db()
        assert produto.quantidade_atual == 5

        # Verifica que a mensagem de erro é informativa
        assert "insuficiente" in str(exc_info.value).lower() or \
               "quantidade" in str(exc_info.value).lower()

    def test_quantidade_zero_invalida(self):
        """
        REGRA: Quantidade zero não é permitida em movimentações.
        """
        usuario = UserFactory()
        produto = ProdutoFactory(quantidade_atual=50)

        with pytest.raises(ValidationError):
            Movimentacao.objects.create(
                produto=produto,
                tipo=Movimentacao.TipoMovimentacao.ENTRADA,
                quantidade=0,
                usuario=usuario,
            )

    def test_movimentacao_nao_editavel(self):
        """
        REGRA: Movimentações não podem ser editadas após criadas.
        """
        usuario = UserFactory()
        produto = ProdutoFactory(quantidade_atual=50)

        movimentacao = Movimentacao.objects.create(
            produto=produto,
            tipo=Movimentacao.TipoMovimentacao.ENTRADA,
            quantidade=10,
            usuario=usuario,
        )

        # Tenta editar — deve lançar ValidationError
        with pytest.raises(ValidationError):
            movimentacao.quantidade = 999
            movimentacao.save()

    def test_str_movimentacao(self):
        """__str__ deve descrever a movimentação de forma legível."""
        usuario = UserFactory()
        produto = ProdutoFactory(nome="Teclado Mecânico", quantidade_atual=50)

        mov = Movimentacao.objects.create(
            produto=produto,
            tipo=Movimentacao.TipoMovimentacao.ENTRADA,
            quantidade=5,
            usuario=usuario,
        )

        resultado = str(mov)
        assert "5" in resultado
        assert "Teclado Mecânico" in resultado

    def test_multiplas_movimentacoes_acumulam_saldo(self):
        """
        Múltiplas movimentações devem acumular o saldo corretamente.
        """
        usuario = UserFactory()
        produto = ProdutoFactory(quantidade_atual=0)

        # Entrada de 100
        Movimentacao.objects.create(
            produto=produto, tipo="entrada", quantidade=100, usuario=usuario
        )
        # Saída de 30
        Movimentacao.objects.create(
            produto=produto, tipo="saida", quantidade=30, usuario=usuario
        )
        # Entrada de 20
        Movimentacao.objects.create(
            produto=produto, tipo="entrada", quantidade=20, usuario=usuario
        )
        # Saída de 15
        Movimentacao.objects.create(
            produto=produto, tipo="saida", quantidade=15, usuario=usuario
        )

        produto.refresh_from_db()
        # 0 + 100 - 30 + 20 - 15 = 75
        assert produto.quantidade_atual == 75
