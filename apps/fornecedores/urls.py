from django.urls import path
from . import views

app_name = "fornecedores"

urlpatterns = [
    path("", views.FornecedorListView.as_view(), name="lista"),
    path("novo/", views.FornecedorCreateView.as_view(), name="criar"),
    path("<int:pk>/editar/", views.FornecedorUpdateView.as_view(), name="editar"),
    path("<int:pk>/excluir/", views.FornecedorDeleteView.as_view(), name="excluir"),
]
