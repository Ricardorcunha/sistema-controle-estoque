from django import forms
from .models import Categoria

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ["nome", "descricao"]
        widgets = {
            "nome": forms.TextInput(attrs={"class": "form-control", "placeholder": "Nome da categoria"}),
            "descricao": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Descrição opcional"}),
        }
