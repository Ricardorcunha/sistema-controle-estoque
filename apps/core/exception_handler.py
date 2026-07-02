"""
exception_handler.py — Handler global de exceções para a API REST.

O DRF chama este handler para converter exceções em respostas JSON.
Estendemos o handler padrão para tratar exceções do Django que o DRF
não conhece nativamente.
"""

from django.db.models.deletion import ProtectedError
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    Handler customizado que estende o padrão do DRF.

    Trata adicionalmente:
    - ProtectedError: tentativa de excluir objeto com FK protegida → 409
    """
    # Primeiro deixa o DRF tratar o que ele já conhece
    response = exception_handler(exc, context)

    if response is not None:
        return response

    # Trata ProtectedError (ex: deletar Categoria com Produtos vinculados)
    if isinstance(exc, ProtectedError):
        return Response(
            {
                "detail": (
                    "Não é possível excluir este registro pois existem "
                    "outros registros vinculados a ele."
                ),
                "tipo": "protected_error",
            },
            status=status.HTTP_409_CONFLICT,
        )

    return response
