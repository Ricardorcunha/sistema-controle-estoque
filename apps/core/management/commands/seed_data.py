"""
seed_data.py — Comando para popular o banco com dados de exemplo.

Uso:
    python manage.py seed_data

Cria:
    - 1 usuário admin e 1 operador
    - 4 categorias
    - 3 fornecedores
    - 12 produtos
    - Movimentações de entrada e saída para cada produto

Seguro para rodar múltiplas vezes: usa get_or_create em tudo.
"""

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.categorias.models import Categoria
from apps.fornecedores.models import Fornecedor
from apps.movimentacoes.models import Movimentacao
from apps.produtos.models import Produto
from apps.usuarios.models import Usuario


class Command(BaseCommand):
    help = "Popula o banco com dados de exemplo para demonstração"

    def handle(self, *args, **options):
        self.stdout.write("Inserindo dados de exemplo...")

        with transaction.atomic():
            self._criar_usuarios()
            categorias = self._criar_categorias()
            fornecedores = self._criar_fornecedores()
            produtos = self._criar_produtos(categorias, fornecedores)
            self._criar_movimentacoes(produtos)

        self.stdout.write(self.style.SUCCESS("Dados inseridos com sucesso!"))
        self.stdout.write("")
        self.stdout.write("Acesse com:")
        self.stdout.write("  Admin:    usuario=admin      senha=admin123")
        self.stdout.write("  Operador: usuario=operador   senha=operador123")

    # ------------------------------------------------------------------
    # Usuários
    # ------------------------------------------------------------------

    def _criar_usuarios(self):
        admin, created = Usuario.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@estoque.com",
                "first_name": "Administrador",
                "last_name": "Sistema",
                "perfil": "admin",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin123")
            admin.save()
            self.stdout.write("  [+] Usuário admin criado")
        else:
            self.stdout.write("  [ ] Usuário admin já existe")

        operador, created = Usuario.objects.get_or_create(
            username="operador",
            defaults={
                "email": "operador@estoque.com",
                "first_name": "João",
                "last_name": "Operador",
                "perfil": "operador",
            },
        )
        if created:
            operador.set_password("operador123")
            operador.save()
            self.stdout.write("  [+] Usuário operador criado")
        else:
            self.stdout.write("  [ ] Usuário operador já existe")

    # ------------------------------------------------------------------
    # Categorias
    # ------------------------------------------------------------------

    def _criar_categorias(self):
        dados = [
            {"nome": "Eletrônicos", "descricao": "Computadores, periféricos e acessórios eletrônicos"},
            {"nome": "Papelaria", "descricao": "Material de escritório e papelaria em geral"},
            {"nome": "Limpeza", "descricao": "Produtos de limpeza e higiene"},
            {"nome": "Informática", "descricao": "Hardware, cabos e equipamentos de TI"},
        ]

        categorias = {}
        for d in dados:
            obj, created = Categoria.objects.get_or_create(
                nome=d["nome"],
                defaults={"descricao": d["descricao"]},
            )
            categorias[d["nome"]] = obj
            status = "[+]" if created else "[ ]"
            self.stdout.write(f"  {status} Categoria: {d['nome']}")

        return categorias

    # ------------------------------------------------------------------
    # Fornecedores
    # ------------------------------------------------------------------

    def _criar_fornecedores(self):
        dados = [
            {
                "nome": "TechSupply Ltda",
                "cnpj": "12.345.678/0001-90",
                "email": "contato@techsupply.com.br",
                "telefone": "(11) 3456-7890",
            },
            {
                "nome": "Papelaria Central",
                "cnpj": "98.765.432/0001-10",
                "email": "vendas@papelariacentral.com.br",
                "telefone": "(21) 2345-6789",
            },
            {
                "nome": "CleanPro Distribuidora",
                "cnpj": "45.678.901/0001-23",
                "email": "pedidos@cleanpro.com.br",
                "telefone": "(31) 9876-5432",
            },
        ]

        fornecedores = {}
        for d in dados:
            obj, created = Fornecedor.objects.get_or_create(
                cnpj=d["cnpj"],
                defaults={
                    "nome": d["nome"],
                    "email": d["email"],
                    "telefone": d["telefone"],
                },
            )
            fornecedores[d["nome"]] = obj
            status = "[+]" if created else "[ ]"
            self.stdout.write(f"  {status} Fornecedor: {d['nome']}")

        return fornecedores

    # ------------------------------------------------------------------
    # Produtos
    # ------------------------------------------------------------------

    def _criar_produtos(self, categorias, fornecedores):
        tech = fornecedores["TechSupply Ltda"]
        papel = fornecedores["Papelaria Central"]
        clean = fornecedores["CleanPro Distribuidora"]

        eletronicos = categorias["Eletrônicos"]
        papelaria = categorias["Papelaria"]
        limpeza = categorias["Limpeza"]
        informatica = categorias["Informática"]

        dados = [
            # Eletrônicos
            {
                "nome": "Monitor 24\" Full HD",
                "categoria": eletronicos,
                "fornecedor": tech,
                "preco": Decimal("899.90"),
                "quantidade_minima": 5,
            },
            {
                "nome": "Teclado Mecânico USB",
                "categoria": eletronicos,
                "fornecedor": tech,
                "preco": Decimal("249.90"),
                "quantidade_minima": 10,
            },
            {
                "nome": "Mouse Sem Fio",
                "categoria": eletronicos,
                "fornecedor": tech,
                "preco": Decimal("89.90"),
                "quantidade_minima": 15,
            },
            # Informática
            {
                "nome": "Cabo HDMI 2m",
                "categoria": informatica,
                "fornecedor": tech,
                "preco": Decimal("29.90"),
                "quantidade_minima": 20,
            },
            {
                "nome": "Hub USB 4 Portas",
                "categoria": informatica,
                "fornecedor": tech,
                "preco": Decimal("59.90"),
                "quantidade_minima": 8,
            },
            {
                "nome": "Headset com Microfone",
                "categoria": informatica,
                "fornecedor": tech,
                "preco": Decimal("179.90"),
                "quantidade_minima": 6,
            },
            # Papelaria
            {
                "nome": "Resma de Papel A4 500 folhas",
                "categoria": papelaria,
                "fornecedor": papel,
                "preco": Decimal("24.90"),
                "quantidade_minima": 30,
            },
            {
                "nome": "Caneta Esferográfica Azul (cx 12un)",
                "categoria": papelaria,
                "fornecedor": papel,
                "preco": Decimal("12.50"),
                "quantidade_minima": 20,
            },
            {
                "nome": "Pasta Arquivo com Elástico",
                "categoria": papelaria,
                "fornecedor": papel,
                "preco": Decimal("8.90"),
                "quantidade_minima": 25,
            },
            {
                "nome": "Bloco de Notas A5",
                "categoria": papelaria,
                "fornecedor": papel,
                "preco": Decimal("6.90"),
                "quantidade_minima": 40,
            },
            # Limpeza
            {
                "nome": "Álcool 70% 1L",
                "categoria": limpeza,
                "fornecedor": clean,
                "preco": Decimal("14.90"),
                "quantidade_minima": 20,
            },
            {
                "nome": "Papel Toalha (pacote 2 rolos)",
                "categoria": limpeza,
                "fornecedor": clean,
                "preco": Decimal("9.90"),
                "quantidade_minima": 30,
            },
        ]

        produtos = []
        for d in dados:
            obj, created = Produto.objects.get_or_create(
                nome=d["nome"],
                defaults={
                    "categoria": d["categoria"],
                    "fornecedor": d["fornecedor"],
                    "preco": d["preco"],
                    "quantidade_minima": d["quantidade_minima"],
                    "quantidade_atual": 0,
                },
            )
            produtos.append((obj, d["quantidade_minima"], created))
            status = "[+]" if created else "[ ]"
            self.stdout.write(f"  {status} Produto: {d['nome']}")

        return produtos

    # ------------------------------------------------------------------
    # Movimentações
    # ------------------------------------------------------------------

    def _criar_movimentacoes(self, produtos):
        """
        Cria entradas e saídas para deixar o estoque em estados variados:
        - Alguns produtos com estoque normal
        - Alguns abaixo do mínimo (alerta amarelo)
        - Um sem estoque (alerta vermelho)
        """

        # (produto, entrada, saída, observacao_entrada, observacao_saida)
        movs = [
            # Monitor — estoque normal (10 entrada, 3 saída → 7, mín=5)
            (0, 10, 3, "Compra inicial - NF 001", "Entrega TI - OS 101"),
            # Teclado — estoque normal (20 entrada, 6 saída → 14, mín=10)
            (1, 20, 6, "Compra inicial - NF 002", "Distribuição escritório"),
            # Mouse — abaixo do mínimo (20 entrada, 18 saída → 2, mín=15)
            (2, 20, 18, "Compra inicial - NF 003", "Reposição estações de trabalho"),
            # Cabo HDMI — estoque normal (50 entrada, 15 saída → 35, mín=20)
            (3, 50, 15, "Compra inicial - NF 004", "Instalações sala de reunião"),
            # Hub USB — sem estoque (8 entrada, 8 saída → 0, mín=8)
            (4, 8, 8, "Compra inicial - NF 005", "Distribuição completa"),
            # Headset — estoque normal (12 entrada, 2 saída → 10, mín=6)
            (5, 12, 2, "Compra inicial - NF 006", "Suporte ao cliente"),
            # Papel A4 — estoque normal (100 entrada, 40 saída → 60, mín=30)
            (6, 100, 40, "Compra inicial - NF 007", "Consumo mensal"),
            # Caneta — abaixo do mínimo (30 entrada, 25 saída → 5, mín=20)
            (7, 30, 25, "Compra inicial - NF 008", "Distribuição colaboradores"),
            # Pasta arquivo — estoque normal (50 entrada, 10 saída → 40, mín=25)
            (8, 50, 10, "Compra inicial - NF 009", "Organização departamentos"),
            # Bloco de notas — estoque normal (80 entrada, 20 saída → 60, mín=40)
            (9, 80, 20, "Compra inicial - NF 010", "Reuniões trimestrais"),
            # Álcool 70% — abaixo do mínimo (30 entrada, 28 saída → 2, mín=20)
            (10, 30, 28, "Compra inicial - NF 011", "Higienização semanal"),
            # Papel toalha — estoque normal (60 entrada, 15 saída → 45, mín=30)
            (11, 60, 15, "Compra inicial - NF 012", "Reposição banheiros"),
        ]

        admin = Usuario.objects.filter(perfil="admin").first()

        criadas = 0
        for idx, entrada, saida, obs_entrada, obs_saida in movs:
            produto = produtos[idx][0]
            was_new = produtos[idx][2]

            # Só cria movimentações se o produto foi recém-criado
            # (evita duplicar ao rodar o comando mais de uma vez)
            if not was_new:
                continue

            Movimentacao.objects.create(
                produto=produto,
                tipo=Movimentacao.TipoMovimentacao.ENTRADA,
                quantidade=entrada,
                observacao=obs_entrada,
                usuario=admin,
            )
            Movimentacao.objects.create(
                produto=produto,
                tipo=Movimentacao.TipoMovimentacao.SAIDA,
                quantidade=saida,
                observacao=obs_saida,
                usuario=admin,
            )
            criadas += 2

        if criadas:
            self.stdout.write(f"  [+] {criadas} movimentações criadas")
        else:
            self.stdout.write("  [ ] Movimentações já existiam (sem duplicação)")
