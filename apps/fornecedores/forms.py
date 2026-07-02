from django import forms
from .models import Fornecedor


class FornecedorForm(forms.ModelForm):
    class Meta:
        model = Fornecedor
        fields = ["nome", "cnpj", "email", "telefone", "ativo"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Razão social ou nome"}),
            "cnpj": forms.TextInput(attrs={"class": "form-control", "placeholder": "00.000.000/0000-00"}),
            "email": forms.EmailInput(attrs={"class": "form-control", "placeholder": "contato@empresa.com"}),
            "telefone": forms.TextInput(attrs={"class": "form-control", "placeholder": "(11) 00000-0000"}),
            "ativo": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
