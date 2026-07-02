"""
admin.py — Admin customizado para o modelo Usuario.

Estende o UserAdmin padrão do Django para incluir o campo 'perfil'.
Se não fizermos isso, o campo perfil não aparece no admin.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Admin para o modelo Usuario customizado.

    Herda de UserAdmin (não de ModelAdmin) para manter os
    comportamentos especiais do Django para usuários:
    - Formulário de alteração de senha
    - Campos de permissões
    - Seções organizadas
    """

    # Colunas na listagem
    list_display = [
        "username", "email", "nome_completo",
        "perfil", "is_active", "is_staff", "date_joined",
    ]
    list_filter = ["perfil", "is_active", "is_staff"]
    search_fields = ["username", "email", "first_name", "last_name"]
    ordering = ["username"]

    # Adiciona o campo 'perfil' ao formulário de edição
    # fieldsets herda do UserAdmin e adicionamos nossa seção
    fieldsets = UserAdmin.fieldsets + (
        ("Perfil do Sistema", {
            "fields": ("perfil",),
        }),
    )

    # Adiciona 'perfil' ao formulário de criação de novo usuário
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Perfil do Sistema", {
            "fields": ("perfil", "email"),
        }),
    )
