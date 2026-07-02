"""
serializers.py — Serializers de Movimentacao.

Movimentações têm comportamento especial:
- Criação: chama o MovimentacaoService (não o Model diretamente)
- Leitura: retorna dados aninhados com produto e usuário
- Edição/Exclusão: BLOQUEADAS (movimentações são imutáveis)
"""

from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.core.exceptions import (
    EstoqueInsuficienteError,
    MovimentacaoInvalidaError,
    ProdutoInativoError,
)
from apps.produtos.models import Produto

from .models import Movimentacao
from .services import MovimentacaoService

User = get_user_model()


class MovimentacaoSerializer(serializers.ModelSerializer):
    """
    Serializer para LEITURA de Movimentacao.
    Retorna dados completos com produto e usuário aninhados.
    """

    produto_nome = serializers.CharField(source="produto.nome", read_only=True)
    usuario_nome = serializers.CharField(source="usuario.nome_completo", read_only=True)
    tipo_display = serializers.CharField(source="get_tipo_display", read_only=True)

    class Meta:
        model = Movimentacao
        fields = [
            "id",
            "produto",
            "produto_nome",
            "tipo",
            "tipo_display",
            "quantidade",
            "usuario",
            "usuario_nome",
            "observacao",
            "data",
        ]
        read_only_fields = fields  # Todos somente leitura neste serializer


class MovimentacaoCreateSerializer(serializers.Serializer):
    """
    Serializer para CRIAÇÃO de Movimentacao.

    Por que não usar ModelSerializer aqui?
    Porque a criação passa pelo Service (que aplica regras de negócio),
    não diretamente pelo Model. Usar Serializer base dá mais controle.

    O campo 'usuario' é preenchido automaticamente com o usuário logado
    (injetado no método create via context['request']).
    """

    produto = serializers.PrimaryKeyRelatedField(
        queryset=Produto.objects.filter(ativo=True),
        help_text="ID do produto a ser movimentado.",
    )
    tipo = serializers.ChoiceField(
        choices=Movimentacao.TipoMovimentacao.choices,
        help_text="'entrada' para entrada de estoque, 'saida' para saída.",
    )
    quantidade = serializers.IntegerField(
        min_value=1,
        help_text="Quantidade a movimentar. Deve ser maior que zero.",
    )
    observacao = serializers.CharField(
        required=False,
        allow_blank=True,
        default="",
        help_text="Observação opcional sobre a movimentação.",
    )

    def validate(self, attrs: dict) -> dict:
        """
        Validação cruzada entre campos.
        Aqui verificamos regras que dependem de mais de um campo.
        """
        produto = attrs.get("produto")
        tipo = attrs.get("tipo")
        quantidade = attrs.get("quantidade")

        # Verifica estoque suficiente para saída
        if tipo == Movimentacao.TipoMovimentacao.SAIDA and produto and quantidade:
            if quantidade > produto.quantidade_atual:
                raise serializers.ValidationError({
                    "quantidade": (
                        f"Estoque insuficiente. "
                        f"Disponivel: {produto.quantidade_atual} | "
                        f"Solicitado: {quantidade}."
                    )
                })

        return attrs

    def create(self, validated_data: dict) -> Movimentacao:
        """
        Cria a movimentação via Service (não diretamente no Model).

        O usuário logado é obtido do contexto da requisição.
        O DRF injeta o context automaticamente quando o serializer
        é instanciado na ViewSet.
        """
        usuario = self.context["request"].user
        service = MovimentacaoService()

        produto = validated_data["produto"]
        tipo = validated_data["tipo"]
        quantidade = validated_data["quantidade"]
        observacao = validated_data.get("observacao", "")

        try:
            if tipo == Movimentacao.TipoMovimentacao.ENTRADA:
                return service.registrar_entrada(
                    produto=produto,
                    quantidade=quantidade,
                    usuario=usuario,
                    observacao=observacao,
                )
            else:
                return service.registrar_saida(
                    produto=produto,
                    quantidade=quantidade,
                    usuario=usuario,
                    observacao=observacao,
                )
        except EstoqueInsuficienteError as e:
            raise serializers.ValidationError({"quantidade": str(e)})
        except (MovimentacaoInvalidaError, ProdutoInativoError) as e:
            raise serializers.ValidationError({"non_field_errors": str(e)})


class MovimentacaoDetalheSerializer(MovimentacaoSerializer):
    """
    Serializer de leitura detalhada — inclui dados do produto completos.
    Usado no endpoint de detalhe (GET /movimentacoes/{id}/).
    """

    from apps.produtos.serializers import ProdutoSerializer
    produto_detalhe = serializers.SerializerMethodField()

    class Meta(MovimentacaoSerializer.Meta):
        fields = MovimentacaoSerializer.Meta.fields + ["produto_detalhe"]

    def get_produto_detalhe(self, obj: Movimentacao) -> dict:
        from apps.produtos.serializers import ProdutoSerializer
        return ProdutoSerializer(obj.produto, context=self.context).data
