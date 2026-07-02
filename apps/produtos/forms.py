from django import forms
from apps.categorias.models import Categoria
from apps.fornecedores.models import Fornecedor
from .models import Produto


class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ["nome", "categoria", "fornecedor", "preco", "quantidade_minima", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nome do produto",
            }),
            "categoria": forms.Select(attrs={"class": "form-select"}),
            "fornecedor": forms.Select(attrs={"class": "form-select"}),
            "preco": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
                "placeholder": "0.00",
            }),
            "quantidade_minima": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
                "placeholder": "0",
            }),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtra apenas categorias e fornecedores ativos
        self.fields["categoria"].queryset = Categoria.objects.all().order_by("nome")
        self.fields["fornecedor"].queryset = Fornecedor.objects.filter(ativo=True).order_by("nome")
        self.fields["categoria"].empty_label = "-- Selecione uma categoria --"
        self.fields["fornecedor"].empty_label = "-- Selecione um fornecedor --"
