"""
factories.py - Fabricas de objetos para testes com factory_boy.

Por que factory_boy?
- Cria objetos de teste com dados realistas
- Evita repeticao de codigo nos testes (DRY)
- Permite sobrescrever apenas o que e relevante para cada teste

Exemplo de uso:
    produto = ProdutoFactory()
    produto = ProdutoFactory(nome="Notebook Dell")
    produto = ProdutoFactory.build()
"""

import factory
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory

from apps.categorias.models import Categoria
from apps.fornecedores.models import Fornecedor
from apps.produtos.models import Produto

User = get_user_model()


class UserFactory(DjangoModelFactory):
    """Cria usuarios para testes."""

    class Meta:
        model = User
        skip_postgeneration_save = True

    username = factory.Sequence(lambda n: f"usuario_{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@teste.com")
    first_name = factory.Faker("first_name", locale="pt_BR")
    last_name = factory.Faker("last_name", locale="pt_BR")
    is_active = True
    perfil = "operador"

    @factory.post_generation
    def password(obj, create, extracted, **kwargs):
        """Define a senha apos criar o usuario."""
        password = extracted or "senha_teste_123"
        obj.set_password(password)
        if create:
            obj.save()


class CategoriaFactory(DjangoModelFactory):
    """Cria categorias de produtos para testes."""

    class Meta:
        model = Categoria

    nome = factory.Sequence(lambda n: f"Categoria {n}")
    descricao = factory.Faker("sentence", nb_words=6, locale="pt_BR")


class FornecedorFactory(DjangoModelFactory):
    """Cria fornecedores para testes."""

    class Meta:
        model = Fornecedor

    nome = factory.Sequence(lambda n: f"Fornecedor {n} Ltda")
    cnpj = factory.Sequence(lambda n: f"{n:014d}")
    email = factory.LazyAttribute(lambda obj: f"contato{obj.cnpj}@fornecedor.com")
    telefone = "(11) 99999-0000"
    ativo = True


class ProdutoFactory(DjangoModelFactory):
    """Cria produtos para testes."""

    class Meta:
        model = Produto

    nome = factory.Sequence(lambda n: f"Produto {n}")
    categoria = factory.SubFactory(CategoriaFactory)
    fornecedor = factory.SubFactory(FornecedorFactory)
    preco = factory.Faker(
        "pydecimal", left_digits=4, right_digits=2, positive=True
    )
    quantidade_atual = 100
    quantidade_minima = 10
    ativo = True
