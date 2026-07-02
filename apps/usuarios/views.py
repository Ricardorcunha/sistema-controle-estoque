"""
views.py — Views de autenticação do sistema.

Usamos as views built-in do Django para login/logout.
Não reinventamos a roda — o Django já tem views testadas e seguras.

LoginView do Django já faz:
    - Exibir o formulário de login
    - Validar credenciais
    - Criar a sessão do usuário
    - Redirecionar após login
    - Proteger contra ataques de força bruta (rate limiting no futuro)

Nós apenas customizamos o template e o comportamento pós-login.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.views.generic import UpdateView

from .mixins import AdminRequiredMixin

User = get_user_model()


class CustomLoginView(LoginView):
    """
    View de login customizada.

    Herda toda a lógica do LoginView do Django.
    Apenas customizamos o template e o redirect.

    template_name: Aponta para nosso template HTML.
    redirect_authenticated_user: Se já logado, redireciona ao invés
        de mostrar o formulário de login novamente.
    """

    template_name = "usuarios/login.html"
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        """Adiciona dados extras ao contexto do template."""
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Login — Sistema de Estoque"
        return context


class CustomLogoutView(LogoutView):
    """
    View de logout.

    O Django 5.x exige POST para logout (proteção CSRF).
    O next_page define para onde redirecionar após logout.
    """

    next_page = reverse_lazy("usuarios:login")


class PerfilUsuarioView(LoginRequiredMixin, UpdateView):
    """
    View para o usuário editar seu próprio perfil.

    LoginRequiredMixin garante que apenas usuários autenticados acessem.
    UpdateView gerencia o formulário de edição automaticamente.
    """

    model = User
    fields = ["first_name", "last_name", "email"]
    template_name = "usuarios/perfil.html"
    success_url = reverse_lazy("usuarios:perfil")

    def get_object(self):
        """Retorna sempre o usuário logado (não permite editar outros)."""
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Meu Perfil"
        return context
