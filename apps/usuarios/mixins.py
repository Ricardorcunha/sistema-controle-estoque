"""
mixins.py — Mixins de controle de acesso por perfil.

Mixin é uma classe que adiciona comportamento a outras classes via herança múltipla.
No Django, usamos Mixins nas Views para adicionar verificações de permissão.

Exemplo de uso em uma View:
    class ProdutoDeleteView(AdminRequiredMixin, DeleteView):
        model = Produto
        # Apenas admins chegam aqui. Operadores são redirecionados.

Por que Mixin e não decorator?
    Para Class-Based Views (CBV), Mixins são mais elegantes.
    Para Function-Based Views (FBV), decorators são mais simples.
    Usaremos CBV neste projeto (padrão em Django moderno).

Hierarquia de herança (ordem importa!):
    class MinhaView(AdminRequiredMixin, LoginRequiredMixin, View):
    Mixin customizado → LoginRequired → View base
    O MRO (Method Resolution Order) do Python garante a ordem correta.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied


class AdminRequiredMixin(LoginRequiredMixin):
    """
    Mixin que exige perfil de Administrador.

    Herda de LoginRequiredMixin: primeiro verifica se está logado,
    depois verifica se tem perfil admin.

    Comportamento:
        - Não autenticado → redireciona para /login/
        - Autenticado mas sem perfil admin → levanta PermissionDenied (403)
        - Admin → prossegue normalmente
    """

    def dispatch(self, request, *args, **kwargs):
        """
        dispatch() é chamado antes de qualquer método (get, post, etc.).
        É o ponto ideal para verificações de acesso.
        """
        # LoginRequiredMixin já verifica autenticação
        response = super().dispatch(request, *args, **kwargs)

        # Se o usuário está autenticado mas não é admin
        if request.user.is_authenticated and not request.user.is_admin():
            raise PermissionDenied(
                "Você não tem permissão para acessar esta página. "
                "É necessário perfil de Administrador."
            )

        return response


class OperadorOuAdminMixin(LoginRequiredMixin):
    """
    Mixin que permite acesso a Operadores e Administradores.
    Basicamente: qualquer usuário autenticado.

    Útil para views que qualquer usuário logado pode acessar,
    mas que exigem autenticação (evita acesso anônimo).
    """
    # LoginRequiredMixin já faz todo o trabalho aqui.
    # Este Mixin existe para documentar a intenção e permitir
    # expansão futura (ex: verificar se a conta está ativa).
    pass
