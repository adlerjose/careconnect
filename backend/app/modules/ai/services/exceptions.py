"""Exceções customizadas da camada de serviços de Inteligência Artificial."""


class AIModuleError(Exception):
    """Exceção base para erros originados no módulo de IA."""
    pass


class AIProviderError(AIModuleError):
    """Falha genérica de comunicação, invocação ou resposta de um provedor de IA."""
    pass


class AIProviderNotConfiguredError(AIProviderError):
    """Lançada quando o provedor de IA requisitado não está configurado para execução real."""
    pass


class AIExtractionError(AIModuleError):
    """Falha durante o parsing ou estruturação dos dados clínicos extraídos."""
    pass
