"""
models.py — Modelo de Usuário customizado.

Estende o AbstractUser do Django adicionando o campo 'perfil'.
Todos os campos padrão são mantidos: username, email, password,
first_name, last_name, is_active, is_staff, date_joined, etc.

Por que AbstractUser e não User?
    AbstractUser é a classe base sem tabela própria.
    User (padrão do Django) já tem uma tabela e não pode ser substituído
    facilmente depois que o projeto começa.
    Ao usar AbstractUser, criamos nossa própria tabela desde o início.

Como referenciar este modelo no código:
    # Nunca importe User diretamente:
    from django.contrib.auth.models import User  ← ERRADO

    # Sempre use get_user_model() ou settings.AUTH_USER_MODEL:
    from django.contrib.auth import get_user_model
    User = get_user_model()                       ← CORRETO

    # Em ForeignKey (models.py):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, ...)  ← CORRETO
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    """
    Modelo de usuário customizado do sistema de estoque.

    Herda de AbstractUser todos os campos padrão do Django:
        - username, password, email
        - first_name, last_name
        - is_active, is_staff, is_superuser
        - date_joined, last_login
        - groups, user_permissions

    Adiciona:
        - perfil: define o nível de acesso no sistema
    """

    class Perfil(models.TextChoices):
        """
        Enum de perfis de usuário.

        ADMIN    → acesso total: pode criar/editar/excluir tudo
        OPERADOR → acesso limitado: pode registrar movimentações,
                   consultar produtos, mas não pode excluir ou
                   acessar configurações
        """
        ADMIN = "admin", "Administrador"
        OPERADOR = "operador", "Operador"

    perfil = models.CharField(
        max_length=10,
        choices=Perfil.choices,
        default=Perfil.OPERADOR,    # Por segurança, padrão é o perfil mais restrito
        verbose_name="Perfil",
        help_text="Define o nível de acesso do usuário no sistema.",
    )

    # Campo email único — no padrão do Django ele permite duplicatas
    email = models.EmailField(
        unique=True,
        verbose_name="E-mail",
    )

    class Meta:
        db_table = "usuarios_usuario"
        verbose_name = "Usuário"
        verbose_name_plural = "Usuários"
        ordering = ["username"]

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.get_perfil_display()})"

    # ------------------------------------------------------------------
    # Métodos de verificação de perfil
    # Usar métodos em vez de comparar strings diretamente evita typos:
    #   if usuario.is_admin():  ← limpo
    #   if usuario.perfil == "admin":  ← frágil
    # ------------------------------------------------------------------

    def is_admin(self) -> bool:
        """Retorna True se o usuário tem perfil de Administrador."""
        return self.perfil == self.Perfil.ADMIN

    def is_operador(self) -> bool:
        """Retorna True se o usuário tem perfil de Operador."""
        return self.perfil == self.Perfil.OPERADOR

    @property
    def nome_completo(self) -> str:
        """Retorna o nome completo ou o username se não houver nome."""
        return self.get_full_name() or self.username
