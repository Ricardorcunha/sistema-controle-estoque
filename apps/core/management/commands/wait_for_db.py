"""
wait_for_db.py — Management command para aguardar o PostgreSQL ficar disponível.

Por que isso é necessário?
O Docker sobe os containers em paralelo. O container 'web' pode tentar
conectar ao banco antes do PostgreSQL estar pronto para aceitar conexões.
Este comando faz o Django "esperar" até o banco responder.

Uso (no docker-compose):
    python manage.py wait_for_db
"""

import time
import logging

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Django management command que aguarda o banco de dados ficar disponível.

    Herdar de BaseCommand é a forma correta de criar comandos customizados no Django.
    O método handle() é obrigatório — é onde a lógica principal fica.
    """

    help = "Aguarda o banco de dados ficar disponível antes de iniciar a aplicação."

    def add_arguments(self, parser) -> None:
        """
        Permite passar argumentos opcionais ao comando.
        Exemplo: python manage.py wait_for_db --timeout 60
        """
        parser.add_argument(
            "--timeout",
            type=int,
            default=60,
            help="Tempo máximo de espera em segundos (padrão: 60)",
        )
        parser.add_argument(
            "--interval",
            type=int,
            default=2,
            help="Intervalo entre tentativas em segundos (padrão: 2)",
        )

    def handle(self, *args, **options) -> None:
        """Lógica principal do comando."""
        timeout: int = options["timeout"]
        interval: int = options["interval"]
        elapsed: int = 0

        self.stdout.write("Aguardando banco de dados...")

        db_conn = connections["default"]

        while elapsed < timeout:
            try:
                # Tenta realizar uma conexão com o banco
                db_conn.ensure_connection()
                self.stdout.write(
                    self.style.SUCCESS(f"Banco de dados disponível após {elapsed}s!")
                )
                return
            except OperationalError:
                self.stdout.write(
                    f"Banco não disponível ainda. Tentando novamente em {interval}s... "
                    f"({elapsed}s / {timeout}s)"
                )
                time.sleep(interval)
                elapsed += interval

        # Se chegou aqui, o timeout foi atingido
        self.stderr.write(
            self.style.ERROR(
                f"Banco de dados não ficou disponível em {timeout} segundos. "
                "Verifique as configurações de conexão."
            )
        )
        raise SystemExit(1)
