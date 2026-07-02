"""
serializers.py — Serializers de Produto.

Usamos dois serializers:
- ProdutoSerializer: escrita (recebe IDs de categoria e fornecedor)
- ProdutoDetalheSerializer: leitura (retorna objetos aninhados com detalhes)

Padrão comum em APIs REST:
  POST /produtos/ → envia categoria=1, fornecedor=2 (IDs)
  GET  /produtos/ → retorna categoria={id, nome}, fornecedor={id, nome, ...}
"""

from rest_framework import serializers

from apps.categorias.serializers import CategoriaSerializer
from apps.fornecedores.serializers import FornecedorResumoSerializer

from .models import Produto


class ProdutoSerializer(serializers.ModelSerializer):
    """
    Serializer para CRIAÇÃO e EDIÇÃO de Produto.
    Recebe categoria e fornecedor como IDs (PrimaryKeyRelatedField padrão).
    """

    # Campos calculados — somente leitura
    status_estoque = serializers.CharField(read_only=True)
    valor_total_estoque = serializers.DecimalField(
        max_digits=12, decimal_places=2, read_only=True
    )
    esta_abaixo_do_minimo = serializers.SerializerMethodField()

    def get_esta_abaixo_do_minimo(self, obj) -> bool:
        return obj.esta_abaixo_do_minimo()

    class Meta:
        model = Produto
        fields = [
            "id",
            "nome",
            "categoria",
            "fornecedor",
            "preco",
            "quantidade_atual",
            "quantidade_minima",
            "ativo",
            "status_estoque",
            "valor_total_estoque",
            "esta_abaixo_do_minimo",
            "criado_em",
            "atualizado_em",
        ]
        read_only_fields = [
            "id",
            "quantidade_atual",   # Atualizado apenas via Movimentacao
            "status_estoque",
            "valor_total_estoque",
            "esta_abaixo_do_minimo",
            "criado_em",
            "atualizado_em",
        ]

    def validate_preco(self, value):
        """Preço deve ser positivo."""
        if value <= 0:
            raise serializers.ValidationError("O preço deve ser maior que zero.")
        return value

    def validate_quantidade_minima(self, value):
        """Quantidade mínima não pode ser negativa."""
        if value < 0:
            raise serializers.ValidationError(
                "A quantidade mínima não pode ser negativa."
            )
        return value


class ProdutoDetalheSerializer(ProdutoSerializer):
    """
    Serializer para LEITURA de Produto com dados aninhados.
    Usado nos endpoints GET para retornar os detalhes completos
    de categoria e fornecedor sem precisar de requisições extras.

    Estratégia: herda ProdutoSerializer e sobrescreve os campos FK
    para usar serializers aninhados em vez de IDs simples.
    """

    categoria = CategoriaSerializer(read_only=True)
    fornecedor = FornecedorResumoSerializer(read_only=True)
