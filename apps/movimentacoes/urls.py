from django.urls import path
from . import views

app_name = "movimentacoes"

urlpatterns = [
    path("", views.MovimentacaoListView.as_view(), name="lista"),
    path("nova/", views.MovimentacaoCreateView.as_view(), name="criar"),
]
