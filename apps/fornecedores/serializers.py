"""
serializers.py — Serializers de Fornecedor.
"""

from rest_framework import serializers

from .models import Fornecedor


class FornecedorSerializer(serializers.ModelSerializer):
    """Serializer completo de Fornecedor."""

    cnpj_formatado = serializers.CharField(
        read_only=True,
        help_text="CNPJ formatado com máscara: 00.000.000/0000-00"
    )
    total_produtos = serializers.SerializerMethodField()

    class Meta:
        model = Fornecedor
        fields = [
            "id",
            "nome",
            "cnpj",
            "cnpj_formatado",
            "telefone",
            "email",
            "ativo",
            "total_produtos",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = [
            "id", "cnpj_formatado", "total_produtos",
            "criado_em", "atualizado_em",
        ]

    def get_total_produtos(self, obj: Fornecedor) -> int:
        return obj.produtos.count()

    def validate_cnpj(self, value: str) -> str:
        """Remove formatação e valida o CNPJ."""
        digits = "".join(filter(str.isdigit, value))
        if len(digits) != 14:
            raise serializers.ValidationError(
                "CNPJ deve conter exatamente 14 dígitos numéricos."
            )
        return value


class FornecedorResumoSerializer(serializers.ModelSerializer):
    """
    Serializer resumido de Fornecedor.
    Usado quando Fornecedor é exibido dentro de outro serializer (ex: Produto).
    Evita retornar todos os campos desnecessariamente.
    """

    class Meta:
        model = Fornecedor
        fields = ["id", "nome", "cnpj_formatado", "email"]
        read_only_fields = fields
