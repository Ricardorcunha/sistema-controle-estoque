"""
permissions.py — Permissões customizadas para a API REST.

No DRF, permissões são classes que respondem a pergunta:
"Este usuário tem permissão para fazer esta requisição?"

Fluxo de uma requisição:
    1. Autenticação (quem é você? → JWT)
    2. Permissão    (o que você pode fazer? → estas classes)
    3. View         (processa a requisição)

Permissões padrão do DRF que já usamos:
    - IsAuthenticated: usuário deve estar logado
    - IsAdminUser: usuário deve ser staff (is_staff=True)

Nossas permissões customizadas:
    - IsAdminPerfil: usuário deve ter perfil='admin' no nosso sistema
    - IsAdminOrReadOnly: admin pode tudo, outros só leitura
"""

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminPerfil(BasePermission):
    """
    Permite acesso apenas a usuários com perfil 'admin' no sistema.

    Diferente de IsAdminUser (que verifica is_staff),
    esta permissão verifica nosso campo 'perfil' customizado.

    Retorna 403 Forbidden se o usuário não for admin.
    """

    message = "Acesso negado. É necessário perfil de Administrador."

    def has_permission(self, request, view) -> bool:
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin()
        )


class IsAdminOrReadOnly(BasePermission):
    """
    Leitura: qualquer usuário autenticado.
    Escrita (POST, PUT, PATCH, DELETE): apenas admins.

    SAFE_METHODS = ('GET', 'HEAD', 'OPTIONS') — métodos que não alteram dados.

    Uso típico:
        - Operador pode listar e ver detalhes de qualquer recurso
        - Apenas admin pode criar, editar ou excluir
    """

    message = "Acesso negado. Operação de escrita requer perfil de Administrador."

    def has_permission(self, request, view) -> bool:
        if not request.user or not request.user.is_authenticated:
            return False
        # Métodos de leitura: todos os autenticados
        if request.method in SAFE_METHODS:
            return True
        # Métodos de escrita: apenas admin
        return request.user.is_admin()


class IsOwnerOrAdmin(BasePermission):
    """
    Permissão a nível de objeto (has_object_permission).

    O usuário só pode ver/editar seu próprio objeto,
    a menos que seja admin (que pode ver/editar qualquer um).

    Usado principalmente no endpoint de perfil do usuário.
    """

    message = "Você não tem permissão para acessar este recurso."

    def has_object_permission(self, request, view, obj) -> bool:
        # Admin pode tudo
        if request.user.is_admin():
            return True
        # Usuário comum só acessa seu próprio objeto
        return obj == request.user
