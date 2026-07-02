"""
exceptions.py — Exceções de domínio do sistema de estoque.

Por que criar exceções customizadas?
1. Semântica clara: o nome da exceção comunica o problema
2. Fácil de capturar especificamente: except EstoqueInsuficienteError
3. Podem carregar dados contextuais (produto, quantidade etc.)
4. Separa erros de negócio de erros técnicos do Python/Django

Hierarquia:
    Exception
    └── EstoqueBaseError          ← base de todas as nossas exceções
        ├── EstoqueInsuficienteError
        ├── MovimentacaoInvalidaError
        └── ProdutoInativoError
"""


class EstoqueBaseError(Exception):
    """
    Classe base para todas as exceções de domínio do sistema de estoque.

    Herdar de Exception e criar uma base própria permite:
    - Capturar qualquer erro do sistema com: except EstoqueBaseError
    - Capturar erros específicos com: except EstoqueInsuficienteError
    """

    def __init__(self, message: str = "Erro no sistema de estoque.") -> None:
        self.message = message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


class EstoqueInsuficienteError(EstoqueBaseError):
    """
    Lançada quando uma saída tentaria deixar o estoque negativo.

    Atributos:
        produto_nome: Nome do produto afetado.
        disponivel: Quantidade disponível no estoque.
        solicitado: Quantidade solicitada na saída.
    """

    def __init__(self, produto_nome: str, disponivel: int, solicitado: int) -> None:
        self.produto_nome = produto_nome
        self.disponivel = disponivel
        self.solicitado = solicitado
        message = (
            f"Estoque insuficiente para '{produto_nome}'. "
            f"Disponível: {disponivel} | Solicitado: {solicitado}."
        )
        super().__init__(message)


class MovimentacaoInvalidaError(EstoqueBaseError):
    """
    Lançada quando uma movimentação tem dados inválidos.
    Ex: quantidade zero, tipo inválido, produto inativo.
    """

    def __init__(self, message: str = "Movimentação inválida.") -> None:
        super().__init__(message)


class ProdutoInativoError(EstoqueBaseError):
    """
    Lançada quando se tenta movimentar um produto inativo.
    """

    def __init__(self, produto_nome: str) -> None:
        self.produto_nome = produto_nome
        super().__init__(f"O produto '{produto_nome}' está inativo e não pode ser movimentado.")
