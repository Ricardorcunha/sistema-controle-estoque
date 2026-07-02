from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from apps.usuarios.mixins import AdminRequiredMixin
from .forms import ProdutoForm
from .models import Produto


class ProdutoListView(LoginRequiredMixin, ListView):
    model = Produto
    template_name = "produtos/lista.html"
    context_object_name = "produtos"
    paginate_by = 15

    def get_queryset(self):
        qs = super().get_queryset().select_related("categoria", "fornecedor")
        q = self.request.GET.get("q", "")
        categoria = self.request.GET.get("categoria", "")
        status = self.request.GET.get("status", "")

        if q:
            qs = qs.filter(nome__icontains=q)
        if categoria:
            qs = qs.filter(categoria_id=categoria)
        if status == "ativo":
            qs = qs.filter(ativo=True)
        elif status == "inativo":
            qs = qs.filter(ativo=False)
        elif status == "critico":
            from django.db.models import F
            qs = qs.filter(ativo=True, quantidade_atual__lt=F("quantidade_minima"))
        elif status == "sem_estoque":
            qs = qs.filter(ativo=True, quantidade_atual=0)

        return qs

    def get_context_data(self, **kwargs):
        from apps.categorias.models import Categoria
        context = super().get_context_data(**kwargs)
        context["q"] = self.request.GET.get("q", "")
        context["status"] = self.request.GET.get("status", "")
        context["categoria_selecionada"] = self.request.GET.get("categoria", "")
        context["categorias"] = Categoria.objects.all().order_by("nome")
        return context


class ProdutoDetailView(LoginRequiredMixin, DetailView):
    model = Produto
    template_name = "produtos/detalhe.html"
    context_object_name = "produto"

    def get_queryset(self):
        return super().get_queryset().select_related("categoria", "fornecedor")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movimentacoes"] = (
            self.object.movimentacoes.all()
            .select_related("usuario")
            .order_by("-data")[:10]
        )
        return context


class ProdutoCreateView(AdminRequiredMixin, CreateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "produtos/form.html"
    success_url = reverse_lazy("produtos:lista")

    def form_valid(self, form):
        messages.success(self.request, "Produto criado com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Novo Produto"
        context["botao"] = "Salvar"
        return context


class ProdutoUpdateView(AdminRequiredMixin, UpdateView):
    model = Produto
    form_class = ProdutoForm
    template_name = "produtos/form.html"

    def get_success_url(self):
        return reverse_lazy("produtos:detalhe", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, "Produto atualizado com sucesso!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = f"Editar: {self.object.nome}"
        context["botao"] = "Salvar Alterações"
        return context


class ProdutoDeleteView(AdminRequiredMixin, DeleteView):
    model = Produto
    template_name = "produtos/confirmar_exclusao.html"
    success_url = reverse_lazy("produtos:lista")

    def form_valid(self, form):
        try:
            messages.success(self.request, "Produto excluído com sucesso!")
            return super().form_valid(form)
        except Exception:
            messages.error(
                self.request,
                "Não é possível excluir: há movimentações vinculadas a este produto.",
            )
            return self.render_to_response(self.get_context_data())
