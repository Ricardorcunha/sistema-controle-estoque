"""
apps.py — Configuração da app 'core'.

A app core é o coração do projeto:
- Abriga utilitários compartilhados entre todas as outras apps
- Management commands globais (como wait_for_db)
- Mixins, helpers, exceptions base
- Não possui models próprios
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    verbose_name = "Core"
