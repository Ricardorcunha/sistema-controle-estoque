"""
api_views.py — ViewSets da API para Usuario.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from apps.api.permissions import IsAdminPerfil, IsOwnerOrAdmin

from .models import Usuario
from .serializers import (
    UsuarioSerializer,
    UsuarioCreateSerializer,
    AlterarSenhaSerializer,
)


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para Usuario.

    Permissões:
        - Listar/criar/excluir: apenas admins
        - Ver/editar o próprio perfil: qualquer autenticado
    """

    queryset = Usuario.objects.all()
    permission_classes = [IsAuthenticated, IsAdminPerfil]

    def get_serializer_class(self):
        if self.action == "create":
            return UsuarioCreateSerializer
        return UsuarioSerializer

    def get_permissions(self):
        """
        Permissões diferentes por action.

        get_permissions() permite customizar permissões por ação
        em vez de aplicar a mesma permissão a tudo.
        """
        if self.action in ("me", "alterar_senha"):
            # Qualquer usuário autenticado pode ver/editar seu próprio perfil
            return [IsAuthenticated()]
        # Tudo mais: apenas admin
        return [IsAuthenticated(), IsAdminPerfil()]

    @action(detail=False, methods=["get", "patch"], url_path="me")
    def me(self, request: Request) -> Response:
        """
        Retorna ou atualiza o perfil do usuário autenticado.
        GET  /api/v1/usuarios/me/ → ver meu perfil
        PATCH /api/v1/usuarios/me/ → editar meu perfil
        """
        if request.method == "GET":
            serializer = UsuarioSerializer(request.user, context={"request": request})
            return Response(serializer.data)

        serializer = UsuarioSerializer(
            request.user,
            data=request.data,
            partial=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=False, methods=["post"], url_path="alterar-senha")
    def alterar_senha(self, request: Request) -> Response:
        """
        Altera a senha do usuário autenticado.
        POST /api/v1/usuarios/alterar-senha/
        """
        serializer = AlterarSenhaSerializer(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": "Senha alterada com sucesso."},
            status=status.HTTP_200_OK,
        )
