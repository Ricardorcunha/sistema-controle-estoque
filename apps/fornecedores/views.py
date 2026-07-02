from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView

from apps.usuarios.mixins import AdminRequiredMixin
from .forms import FornecedorForm
from .models import Fornecedor


class FornecedorListView(LoginRequiredMixin, ListView):
    model = Fornecedor
    template_name = "fornecedores/lista.html"
    context_object_name = "fornecedores"
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset()
        q = self.request.GET.get("q", "")
        status = self.request.GET.get("status", "")
        if q:
            qs = qs.filter(nome__icontains=q)
        if status == "ativos":
            qs = qs.filter(ativo=True)
        elif status == "inativos":
            qs = qs.filter(ativo=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["status"] = self.request.GET.get("status", "")
        return context


class FornecedorCreateView(AdminRequiredMixin, CreateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "fornecedores/form.html"
    success_url = reverse_lazy("fornecedores:lista")

    def form_valid(self, form):
        messages.success(self.request, "Fornecedor criado com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Novo Fornecedor"
        context["botao"] = "Salvar"
        return context


class FornecedorUpdateView(AdminRequiredMixin, UpdateView):
    model = Fornecedor
    form_class = FornecedorForm
    template_name = "fornecedores/form.html"
    success_url = reverse_lazy("fornecedores:lista")

    def form_valid(self, form):
        messages.success(self.request, "Fornecedor atualizado com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = f"Editar: {self.object.nome}"
        context["botao"] = "Salvar Alterações"
        return context


class FornecedorDeleteView(AdminRequiredMixin, DeleteView):
    model = Fornecedor
    template_name = "fornecedores/confirmar_exclusao.html"
    success_url = reverse_lazy("fornecedores:lista")

    def form_valid(self, form):
        try:
            messages.success(self.request, "Fornecedor excluído com sucesso!")
            return super().form_valid(form)
        except Exception:
            messages.error(
                self.request,
                "Não é possível excluir: há produtos vinculados a este fornecedor.",
            )
            return self.render_to_response(self.get_context_data())
