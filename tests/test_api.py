"""
test_api.py — Testes dos endpoints da API REST.

APIClient do DRF simula requisições HTTP sem precisar de servidor real.
force_authenticate() autentica o cliente sem passar pelo JWT.
"""

import pytest
from decimal import Decimal
from rest_framework.test import APIClient
from rest_framework import status

from apps.movimentacoes.models import Movimentacao

from .factories import (
    CategoriaFactory,
    FornecedorFactory,
    ProdutoFactory,
    UserFactory,
)


@pytest.fixture
def api_client():
    """Fixture: cliente HTTP para testes de API."""
    return APIClient()


@pytest.fixture
def admin_client(api_client):
    """Fixture: cliente autenticado como administrador."""
    admin = UserFactory(perfil="admin")
    api_client.force_authenticate(user=admin)
    return api_client, admin


@pytest.fixture
def operador_client(api_client):
    """Fixture: cliente autenticado como operador."""
    operador = UserFactory(perfil="operador")
    api_client.force_authenticate(user=operador)
    return api_client, operador


# ===========================================================================
# TESTES — JWT Authentication
# ===========================================================================

@pytest.mark.django_db
class TestJWTAuth:
    """Testes para autenticação JWT."""

    def test_obter_token_com_credenciais_validas(self, api_client):
        """POST /api/v1/auth/token/ com credenciais válidas retorna tokens."""
        usuario = UserFactory()
        usuario.set_password("senha_teste_123")
        usuario.save()

        response = api_client.post("/api/v1/auth/token/", {
            "username": usuario.username,
            "password": "senha_teste_123",
        })

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "refresh" in response.data

    def test_obter_token_credenciais_invalidas(self, api_client):
        """POST com senha errada retorna 401."""
        UserFactory(username="usuario_teste")

        response = api_client.post("/api/v1/auth/token/", {
            "username": "usuario_teste",
            "password": "senha_errada",
        })

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_endpoint_protegido_sem_token(self, api_client):
        """Endpoint sem autenticação retorna 401."""
        response = api_client.get("/api/v1/categorias/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_endpoint_com_token_valido(self, api_client):
        """Endpoint com JWT válido retorna 200."""
        usuario = UserFactory()
        usuario.set_password("senha123")
        usuario.save()

        # Obtém o token
        token_response = api_client.post("/api/v1/auth/token/", {
            "username": usuario.username,
            "password": "senha123",
        })
        token = token_response.data["access"]

        # Usa o token no header
        api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = api_client.get("/api/v1/categorias/")
        assert response.status_code == status.HTTP_200_OK


# ===========================================================================
# TESTES — Categorias
# ===========================================================================

@pytest.mark.django_db
class TestCategoriaAPI:
    """Testes para o endpoint /api/v1/categorias/."""

    def test_listar_categorias(self, admin_client):
        """GET /api/v1/categorias/ retorna lista paginada."""
        client, _ = admin_client
        CategoriaFactory.create_batch(3)

        response = client.get("/api/v1/categorias/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_criar_categoria_como_admin(self, admin_client):
        """Admin pode criar categoria."""
        client, _ = admin_client

        response = client.post("/api/v1/categorias/", {"nome": "Eletrônicos"})

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["nome"] == "Eletrônicos"

    def test_criar_categoria_como_operador_bloqueado(self, operador_client):
        """Operador NÃO pode criar categoria (403)."""
        client, _ = operador_client

        response = client.post("/api/v1/categorias/", {"nome": "Nova Categoria"})

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_operador_pode_listar_categorias(self, operador_client):
        """Operador PODE listar categorias (somente leitura)."""
        client, _ = operador_client
        CategoriaFactory.create_batch(2)

        response = client.get("/api/v1/categorias/")

        assert response.status_code == status.HTTP_200_OK

    def test_buscar_categoria_por_nome(self, admin_client):
        """Busca por ?search=nome filtra corretamente."""
        client, _ = admin_client
        CategoriaFactory(nome="Eletrônicos")
        CategoriaFactory(nome="Alimentos")

        response = client.get("/api/v1/categorias/?search=Eletr")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1
        assert response.data["results"][0]["nome"] == "Eletrônicos"

    def test_deletar_categoria_como_admin(self, admin_client):
        """Admin pode deletar categoria sem produtos."""
        client, _ = admin_client
        categoria = CategoriaFactory()

        response = client.delete(f"/api/v1/categorias/{categoria.pk}/")

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_deletar_categoria_com_produto_bloqueado(self, admin_client):
        """Não deve deletar categoria vinculada a produto (PROTECT)."""
        client, _ = admin_client
        produto = ProdutoFactory()

        response = client.delete(f"/api/v1/categorias/{produto.categoria.pk}/")

        assert response.status_code == status.HTTP_409_CONFLICT


# ===========================================================================
# TESTES — Produtos
# ===========================================================================

@pytest.mark.django_db
class TestProdutoAPI:
    """Testes para o endpoint /api/v1/produtos/."""

    def test_listar_produtos(self, admin_client):
        """GET /api/v1/produtos/ retorna lista."""
        client, _ = admin_client
        ProdutoFactory.create_batch(3)

        response = client.get("/api/v1/produtos/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 3

    def test_criar_produto(self, admin_client):
        """Admin pode criar produto."""
        client, _ = admin_client
        categoria = CategoriaFactory()
        fornecedor = FornecedorFactory()

        response = client.post("/api/v1/produtos/", {
            "nome": "Notebook Dell",
            "categoria": categoria.pk,
            "fornecedor": fornecedor.pk,
            "preco": "3500.00",
            "quantidade_minima": 5,
        })

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["nome"] == "Notebook Dell"
        assert response.data["quantidade_atual"] == 0

    def test_produtos_abaixo_do_minimo(self, admin_client):
        """GET /api/v1/produtos/abaixo-do-minimo/ lista produtos críticos."""
        client, _ = admin_client
        ProdutoFactory(quantidade_atual=2, quantidade_minima=10)
        ProdutoFactory(quantidade_atual=50, quantidade_minima=10)

        response = client.get("/api/v1/produtos/abaixo-do-minimo/")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_filtro_por_categoria(self, admin_client):
        """Filtra produtos por categoria."""
        client, _ = admin_client
        cat1 = CategoriaFactory()
        cat2 = CategoriaFactory()
        ProdutoFactory(categoria=cat1)
        ProdutoFactory(categoria=cat1)
        ProdutoFactory(categoria=cat2)

        response = client.get(f"/api/v1/produtos/?categoria={cat1.pk}")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 2


# ===========================================================================
# TESTES — Movimentações
# ===========================================================================

@pytest.mark.django_db
class TestMovimentacaoAPI:
    """Testes para o endpoint /api/v1/movimentacoes/."""

    def test_registrar_entrada(self, admin_client):
        """POST /api/v1/movimentacoes/ com tipo=entrada aumenta estoque."""
        client, usuario = admin_client
        produto = ProdutoFactory(quantidade_atual=10)

        response = client.post("/api/v1/movimentacoes/", {
            "produto": produto.pk,
            "tipo": "entrada",
            "quantidade": 50,
            "observacao": "Compra via API",
        })

        assert response.status_code == status.HTTP_201_CREATED
        produto.refresh_from_db()
        assert produto.quantidade_atual == 60

    def test_registrar_saida_valida(self, admin_client):
        """POST com tipo=saida válida diminui estoque."""
        client, _ = admin_client
        produto = ProdutoFactory(quantidade_atual=100)

        response = client.post("/api/v1/movimentacoes/", {
            "produto": produto.pk,
            "tipo": "saida",
            "quantidade": 30,
        })

        assert response.status_code == status.HTTP_201_CREATED
        produto.refresh_from_db()
        assert produto.quantidade_atual == 70

    def test_saida_estoque_insuficiente_retorna_400(self, admin_client):
        """Saída acima do estoque retorna 400 Bad Request."""
        client, _ = admin_client
        produto = ProdutoFactory(quantidade_atual=5)

        response = client.post("/api/v1/movimentacoes/", {
            "produto": produto.pk,
            "tipo": "saida",
            "quantidade": 10,
        })

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        produto.refresh_from_db()
        assert produto.quantidade_atual == 5  # Saldo inalterado

    def test_nao_permite_put_em_movimentacao(self, admin_client):
        """PUT em movimentação retorna 405 Method Not Allowed."""
        client, usuario = admin_client
        produto = ProdutoFactory(quantidade_atual=50)

        mov = Movimentacao.objects.create(
            produto=produto,
            tipo="entrada",
            quantidade=10,
            usuario=usuario,
        )

        response = client.put(f"/api/v1/movimentacoes/{mov.pk}/", {
            "quantidade": 999,
        })

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_dashboard_retorna_estatisticas(self, admin_client):
        """GET /api/v1/movimentacoes/dashboard/ retorna dados do dashboard."""
        client, _ = admin_client

        response = client.get("/api/v1/movimentacoes/dashboard/")

        assert response.status_code == status.HTTP_200_OK
        assert "total_produtos" in response.data
        assert "entradas_hoje" in response.data
        assert "saidas_hoje" in response.data
        assert "produtos_abaixo_minimo" in response.data
