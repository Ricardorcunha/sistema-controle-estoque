"""
models.py — Model de Fornecedor.

Fornecedor é quem abastece o estoque com produtos.
Campos CNPJ, telefone e email são importantes para contato e rastreabilidade.

Design decision: CNPJ armazenado como CharField.
Motivo: CNPJs têm formatação variável (com ou sem máscara).
Armazenamos apenas dígitos na validação, mas exibimos formatado.
"""

from django.db import models


class Fornecedor(models.Model):
    """
    Representa um fornecedor de produtos.

    Atributos:
        nome: Razão social ou nome fantasia do fornecedor.
        cnpj: CNPJ do fornecedor (único, apenas dígitos).
        telefone: Telefone de contato.
        email: E-mail de contato (único).
        ativo: Indica se o fornecedor está ativo. Preferimos desativar a excluir.
        criado_em: Data/hora de criação.
        atualizado_em: Data/hora da última atualização.
    """

    nome = models.CharField(
        max_length=200,
        verbose_name="Nome / Razão Social",
        help_text="Razão social ou nome fantasia do fornecedor.",
    )
    cnpj = models.CharField(
        max_length=18,        # Formato: 00.000.000/0000-00 (18 chars com máscara)
        unique=True,
        verbose_name="CNPJ",
        help_text="CNPJ no formato 00.000.000/0000-00.",
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        default="",
        verbose_name="Telefone",
        help_text="Telefone de contato com DDD.",
    )
    email = models.EmailField(
        unique=True,
        verbose_name="E-mail",
        help_text="E-mail de contato do fornecedor.",
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name="Ativo",
        help_text="Desmarque para desativar o fornecedor sem excluí-lo.",
    )
    criado_em = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Criado em",
    )
    atualizado_em = models.DateTimeField(
        auto_now=True,
        verbose_name="Atualizado em",
    )

    class Meta:
        db_table = "fornecedores_fornecedor"
        ordering = ["nome"]
        verbose_name = "Fornecedor"
        verbose_name_plural = "Fornecedores"

    def __str__(self) -> str:
        return f"{self.nome} ({self.cnpj})"

    @property
    def cnpj_formatado(self) -> str:
        """
        Retorna o CNPJ formatado visualmente: 00.000.000/0000-00.

        Property é um método que se comporta como atributo.
        Não precisa de parênteses para chamar: fornecedor.cnpj_formatado
        """
        digits = "".join(filter(str.isdigit, self.cnpj))
        if len(digits) == 14:
            return f"{digits[:2]}.{digits[2:5]}.{digits[5:8]}/{digits[8:12]}-{digits[12:]}"
        return self.cnpj  # Retorna original se não tiver 14 dígitos
