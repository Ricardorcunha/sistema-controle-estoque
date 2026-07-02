"""
serializers.py — Serializers de Usuario.
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UsuarioSerializer(serializers.ModelSerializer):
    """Serializer de leitura do Usuario."""

    nome_completo = serializers.CharField(read_only=True)
    perfil_display = serializers.CharField(source="get_perfil_display", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "nome_completo",
            "perfil",
            "perfil_display",
            "is_active",
            "date_joined",
        ]
        read_only_fields = ["id", "nome_completo", "perfil_display", "date_joined"]


class UsuarioCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para CRIAÇÃO de usuário via API.
    Trata a senha com segurança (hash via set_password).
    """

    password = serializers.CharField(
        write_only=True,       # Nunca retorna a senha na resposta
        min_length=8,
        style={"input_type": "password"},
        help_text="Mínimo de 8 caracteres.",
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Repita a senha para confirmação.",
    )

    class Meta:
        model = User
        fields = [
            "id", "username", "email",
            "first_name", "last_name",
            "perfil", "password", "password_confirm",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs: dict) -> dict:
        """Verifica se as senhas coincidem."""
        if attrs.get("password") != attrs.pop("password_confirm", None):
            raise serializers.ValidationError({
                "password_confirm": "As senhas não coincidem."
            })
        return attrs

    def create(self, validated_data: dict) -> User:
        """
        Cria o usuário com senha hasheada.
        Nunca salve senhas em texto puro!
        """
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)   # Aplica o hash (bcrypt/PBKDF2)
        user.save()
        return user


class AlterarSenhaSerializer(serializers.Serializer):
    """Serializer para alteração de senha do usuário autenticado."""

    senha_atual = serializers.CharField(write_only=True)
    nova_senha = serializers.CharField(write_only=True, min_length=8)
    confirmar_nova_senha = serializers.CharField(write_only=True)

    def validate(self, attrs: dict) -> dict:
        user = self.context["request"].user

        if not user.check_password(attrs["senha_atual"]):
            raise serializers.ValidationError({
                "senha_atual": "Senha atual incorreta."
            })
        if attrs["nova_senha"] != attrs["confirmar_nova_senha"]:
            raise serializers.ValidationError({
                "confirmar_nova_senha": "As novas senhas não coincidem."
            })
        return attrs

    def save(self) -> None:
        user = self.context["request"].user
        user.set_password(self.validated_data["nova_senha"])
        user.save()
