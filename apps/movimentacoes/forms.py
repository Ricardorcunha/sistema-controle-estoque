from django import forms
from apps.produtos.models import Produto
from .models import Movimentacao


class MovimentacaoForm(forms.ModelForm):
    """
    Formulário de criação de movimentação.

    Diferente dos outros CRUDs, movimentação não tem Update/Delete:
    é imutável por design (auditoria). O formulário serve apenas para
    o CreateView.

    A quantidade_atual é exibida como campo somente-leitura para
    orientar o operador antes de confirmar a saída.
    """

    class Meta:
        model = Movimentacao
        fields = ["produto", "tipo", "quantidade", "observacao"]
        widgets = {
            "produto": forms.Select(attrs={"class": "form-select", "id": "id_produto"}),
            "tipo": forms.Select(attrs={"class": "form-select"}),
            "quantidade": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "1",
                "placeholder": "Ex: 10",
            }),
            "observacao": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Observação opcional (nota fiscal, lote, etc.)",
            }),
        }

    def __init__(self, *args, **kwargs):
        produto_id = kwargs.pop("produto_id", None)
        super().__init__(*args, **kwargs)
        self.fields["produto"].queryset = Produto.objects.filter(ativo=True).order_by("nome")
        self.fields["produto"].empty_label = "-- Selecione um produto --"
        if produto_id:
            try:
                self.fields["produto"].initial = int(produto_id)
            except (ValueError, TypeError):
                pass

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        quantidade = cleaned_data.get("quantidade")
        produto = cleaned_data.get("produto")

        if tipo == Movimentacao.TipoMovimentacao.SAIDA and produto and quantidade:
            if quantidade > produto.quantidade_atual:
                raise forms.ValidationError(
                    f"Estoque insuficiente. Disponível: {produto.quantidade_atual} unidades."
                )
        return cleaned_data
