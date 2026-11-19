"""Exceções customizadas da camada de serviços de Inteligência Artificial."""


class AIModuleError(Exception):
    """Exceção base para erros originados no módulo de IA."""
    pass


class AIProviderError(AIModuleError):
    """Falha genérica de comunicação, invocação ou resposta de um provedor de IA."""
    pass


class AIProviderNotConfiguredError(AIProviderError):
    """Lançada quando o provedor de IA requisitado não está configurado para execução real (ex: falta de chave)."""
    pass


class AIProviderAuthenticationError(AIProviderError):
    """Lançada quando a autenticação com o provedor de IA falha (ex: chave inválida ou revogada)."""
    pass


class AIProviderRateLimitError(AIProviderError):
    """Lançada quando o limite de requisições ou cota do provedor de IA foi atingido."""
    pass


class AIProviderTimeoutError(AIProviderError):
    """Lançada quando uma requisição ao provedor de IA excede o tempo limite configurado."""
    pass


class AIProviderUnavailableError(AIProviderError):
    """Lançada quando o serviço do provedor de IA está temporariamente indisponível ou fora do ar."""
    pass


class AIProviderBlockedError(AIProviderError):
    """Lançada quando a resposta ou requisição foi bloqueada por filtros de segurança ou políticas do modelo."""
    pass


class AIExtractionError(AIModuleError):
    """Falha durante o parsing, estruturação ou validação dos dados clínicos extraídos."""
    pass
