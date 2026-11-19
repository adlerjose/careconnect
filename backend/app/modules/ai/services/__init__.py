"""Serviços e integrações com provedores de Inteligência Artificial."""

from app.modules.ai.services.base_provider import BaseAIProvider
from app.modules.ai.services.exceptions import (
    AIExtractionError,
    AIModuleError,
    AIProviderAuthenticationError,
    AIProviderBlockedError,
    AIProviderError,
    AIProviderNotConfiguredError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)
from app.modules.ai.services.gemini_provider import GeminiProvider

__all__ = [
    "BaseAIProvider",
    "GeminiProvider",
    "AIModuleError",
    "AIProviderError",
    "AIProviderNotConfiguredError",
    "AIProviderAuthenticationError",
    "AIProviderRateLimitError",
    "AIProviderTimeoutError",
    "AIProviderUnavailableError",
    "AIProviderBlockedError",
    "AIExtractionError",
]
