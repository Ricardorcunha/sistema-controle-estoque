"""
serializers.py — Serializers de Categoria.

ModelSerializer gera automaticamente campos a partir do Model.
Precisamos apenas declarar quais campos expor e quais validações adicionar.
"""

from rest_framework import serializers

from .models import Categoria


class CategoriaSerializer(serializers.ModelSerializer):
    """
    Serializer completo de Categoria.

    Campos read_only: calculados, não podem ser enviados pelo cliente.
    total_produtos: contagem calculada via SerializerMethodField.
    """

    total_produtos = serializers.SerializerMethodField(
        help_text="Número de produtos vinculados a esta categoria."
    )

    class Meta:
        model = Categoria
        fields = [
            "id",
            "nome",
            "descricao",
            "total_produtos",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = ["id", "total_produtos", "criado_em", "atualizado_em"]

    def get_total_produtos(self, obj: Categoria) -> int:
        """
        SerializerMethodField: campo calculado dinamicamente.
        O nome do método DEVE ser get_{nome_do_campo}.
        """
        return obj.produtos.count()

    def validate_nome(self, value: str) -> str:
        """
        Validação customizada para o campo 'nome'.
        Métodos validate_{campo} são chamados automaticamente pelo DRF.
        """
        return value.strip().title()  # Remove espaços e capitaliza
