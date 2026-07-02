from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView

from apps.movimentacoes.services import MovimentacaoService
from apps.core.exceptions import EstoqueInsuficienteError, ProdutoInativoError
from .forms import MovimentacaoForm
from .models import Movimentacao


class MovimentacaoListView(LoginRequiredMixin, ListView):
    model = Movimentacao
    template_name = "movimentacoes/lista.html"
    context_object_name = "movimentacoes"
    paginate_by = 20

    def get_queryset(self):
        qs = (
            super().get_queryset()
            .select_related("produto", "usuario")
            .order_by("-data")
        )
        tipo = self.request.GET.get("tipo", "")
        produto_id = self.request.GET.get("produto", "")
        data_inicio = self.request.GET.get("data_inicio", "")
        data_fim = self.request.GET.get("data_fim", "")

        if tipo:
            qs = qs.filter(tipo=tipo)
        if produto_id:
            qs = qs.filter(produto_id=produto_id)
        if data_inicio:
            qs = qs.filter(data__date__gte=data_inicio)
        if data_fim:
            qs = qs.filter(data__date__lte=data_fim)

        return qs

    def get_context_data(self, **kwargs):
        from apps.produtos.models import Produto
        context = super().get_context_data(**kwargs)
        context["tipo"] = self.request.GET.get("tipo", "")
        context["produto_selecionado"] = self.request.GET.get("produto", "")
        context["data_inicio"] = self.request.GET.get("data_inicio", "")
        context["data_fim"] = self.request.GET.get("data_fim", "")
        context["produtos"] = Produto.objects.filter(ativo=True).order_by("nome")
        context["tipos"] = Movimentacao.TipoMovimentacao.choices
        return context


class MovimentacaoCreateView(LoginRequiredMixin, CreateView):
    model = Movimentacao
    form_class = MovimentacaoForm
    template_name = "movimentacoes/form.html"
    success_url = reverse_lazy("movimentacoes:lista")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Passa produto pré-selecionado via querystring (?produto=<id>)
        kwargs["produto_id"] = self.request.GET.get("produto")
        return kwargs

    def form_valid(self, form):
        try:
            produto = form.cleaned_data["produto"]
            tipo = form.cleaned_data["tipo"]
            quantidade = form.cleaned_data["quantidade"]
            observacao = form.cleaned_data.get("observacao", "")

            if tipo == Movimentacao.TipoMovimentacao.ENTRADA:
                MovimentacaoService.registrar_entrada(
                    produto=produto,
                    quantidade=quantidade,
                    usuario=self.request.user,
                    observacao=observacao,
                )
                messages.success(self.request, f"Entrada de {quantidade} unidade(s) de '{produto.nome}' registrada!")
            else:
                MovimentacaoService.registrar_saida(
                    produto=produto,
                    quantidade=quantidade,
                    usuario=self.request.user,
                    observacao=observacao,
                )
                messages.success(self.request, f"Saída de {quantidade} unidade(s) de '{produto.nome}' registrada!")

            return super(CreateView, self).form_valid(form)

        except EstoqueInsuficienteError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)
        except ProdutoInativoError as e:
            messages.error(self.request, str(e))
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["titulo"] = "Nova Movimentação"
        context["botao"] = "Registrar"
        return context
