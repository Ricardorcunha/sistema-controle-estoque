from django.urls import path
from . import views

app_name = "categorias"

urlpatterns = [
    path("", views.CategoriaListView.as_view(), name="lista"),
    path("novo/", views.CategoriaCreateView.as_view(), name="criar"),
    path("<int:pk>/editar/", views.CategoriaUpdateView.as_view(), name="editar"),
    path("<int:pk>/excluir/", views.CategoriaDeleteView.as_view(), name="excluir"),
]
