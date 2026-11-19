import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Configura o sistema central de logs da aplicação.
    Define formato, nível de severidade e saída padrão.
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )

    # Configuração do handler principal (stdout)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(log_format, datefmt="%Y-%m-%d %H:%M:%S"))

    # Configuração do logger raiz da aplicação
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Evita duplicação de handlers caso seja reexecutado
    if not any(isinstance(h, logging.StreamHandler) for h in root_logger.handlers):
        root_logger.addHandler(handler)

    # Configura logger específico da aplicação
    app_logger = logging.getLogger("careconnect")
    app_logger.setLevel(log_level)


def get_logger(name: str = "careconnect") -> logging.Logger:
    """Retorna um logger configurado para o módulo solicitante."""
    return logging.getLogger(name)
