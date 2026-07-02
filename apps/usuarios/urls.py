"""
urls.py — Rotas da app de usuários.

app_name cria um namespace: podemos usar reverse('usuarios:login')
em vez de reverse('login'), evitando conflitos com outras apps.
"""

from django.urls import path

from . import views

app_name = "usuarios"

urlpatterns = [
    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", views.CustomLogoutView.as_view(), name="logout"),
    path("perfil/", views.PerfilUsuarioView.as_view(), name="perfil"),
]
