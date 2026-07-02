from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.usuarios.mixins import AdminRequiredMixin
from .forms import CategoriaForm
from .models import Categoria


class CategoriaListView(LoginRequiredMixin, ListView):
    model = Categoria
    template_name = "categorias/lista.html"
    context_object_name = "categorias"
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(nome__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        return context


class CategoriaCreateView(AdminRequiredMixin, CreateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "categorias/form.html"
    success_url = reverse_lazy("categorias:lista")

    def form_valid(self, form):
        messages.success(self.request, "Categoria criada com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Nova Categoria"
        context["botao"] = "Salvar"
        return context


class CategoriaUpdateView(AdminRequiredMixin, UpdateView):
    model = Categoria
    form_class = CategoriaForm
    template_name = "categorias/form.html"
    success_url = reverse_lazy("categorias:lista")

    def form_valid(self, form):
        messages.success(self.request, "Categoria atualizada com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = f"Editar: {self.object.nome}"
        context["botao"] = "Salvar Alterações"
        return context


class CategoriaDeleteView(AdminRequiredMixin, DeleteView):
    model = Categoria
    template_name = "categorias/confirmar_exclusao.html"
    success_url = reverse_lazy("categorias:lista")

    def form_valid(self, form):
        try:
            messages.success(self.request, "Categoria excluída com sucesso!")
            return super().form_valid(form)
        except Exception:
            messages.error(self.request, "Não é possível excluir: há produtos vinculados a esta categoria.")
            return self.render_to_response(self.get_context_data())
