"""
test_usuarios.py — Testes do modelo de usuário e controle de acesso.
"""

import pytest
from django.contrib.auth import get_user_model

from .factories import UserFactory

User = get_user_model()


@pytest.mark.django_db
class TestUsuarioModel:
    """Testes para o modelo Usuario customizado."""

    def test_criar_usuario_operador(self):
        """Deve criar usuário com perfil operador por padrão."""
        usuario = UserFactory()
        assert usuario.pk is not None
        assert usuario.perfil == "operador"
        assert usuario.is_operador() is True
        assert usuario.is_admin() is False

    def test_criar_usuario_admin(self):
        """Deve criar usuário com perfil admin."""
        admin = UserFactory(perfil="admin")
        assert admin.is_admin() is True
        assert admin.is_operador() is False

    def test_str_com_nome_completo(self):
        """__str__ deve incluir nome completo e perfil."""
        usuario = UserFactory(
            first_name="Ricardo",
            last_name="Cunha",
            perfil="admin",
        )
        resultado = str(usuario)
        assert "Ricardo Cunha" in resultado
        assert "Administrador" in resultado

    def test_str_sem_nome_usa_username(self):
        """__str__ deve usar username quando não há nome completo."""
        usuario = UserFactory(first_name="", last_name="")
        resultado = str(usuario)
        assert usuario.username in resultado

    def test_nome_completo_property(self):
        """Propriedade nome_completo deve retornar nome ou username."""
        usuario = UserFactory(first_name="João", last_name="Silva")
        assert usuario.nome_completo == "João Silva"

    def test_nome_completo_sem_nome_retorna_username(self):
        """Sem nome, nome_completo deve retornar username."""
        usuario = UserFactory(first_name="", last_name="")
        assert usuario.nome_completo == usuario.username

    def test_email_unico(self):
        """Dois usuários não podem ter o mesmo email."""
        UserFactory(email="teste@email.com")
        with pytest.raises(Exception):
            UserFactory(email="teste@email.com")

    def test_perfil_padrao_e_operador(self):
        """O perfil padrão deve ser 'operador' (mais seguro)."""
        usuario = User.objects.create_user(
            username="novousuario",
            password="senha123",
            email="novo@email.com",
        )
        assert usuario.perfil == "operador"


@pytest.mark.django_db
class TestAutenticacaoView:
    """Testes para as views de login/logout."""

    def test_login_page_acessivel(self, client):
        """A página de login deve ser acessível sem autenticação."""
        response = client.get("/login/")
        assert response.status_code == 200

    def test_login_com_credenciais_validas(self, client):
        """Login com usuário e senha corretos deve redirecionar."""
        usuario = UserFactory()
        usuario.set_password("senha_teste_123")
        usuario.save()

        response = client.post("/login/", {
            "username": usuario.username,
            "password": "senha_teste_123",
        })

        # Redireciona após login bem-sucedido
        assert response.status_code == 302

    def test_login_com_credenciais_invalidas(self, client):
        """Login com senha errada deve retornar formulário com erro."""
        UserFactory(username="usuario_teste")

        response = client.post("/login/", {
            "username": "usuario_teste",
            "password": "senha_errada",
        })

        assert response.status_code == 200
        assert response.context["form"].errors

    def test_logout_redireciona_para_login(self, client):
        """Logout deve redirecionar para a página de login."""
        usuario = UserFactory()
        client.force_login(usuario)

        response = client.post("/logout/")
        assert response.status_code == 302
        assert "/login/" in response["Location"]

    def test_usuario_autenticado_nao_ve_login(self, client):
        """Usuário já logado acessando /login/ deve ser redirecionado."""
        usuario = UserFactory()
        client.force_login(usuario)

        response = client.get("/login/")
        # redirect_authenticated_user=True faz o redirecionamento
        assert response.status_code == 302
