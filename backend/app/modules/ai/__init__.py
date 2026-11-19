"""
Módulo de Inteligência Artificial para interpretação e triagem auxiliar via LLM.
Fornece contratos, abstrações de provedores e pipelines de extração clínica.
"""

from app.modules.ai.pipelines import ClinicalExtractionPipeline
from app.modules.ai.schemas import AIMessageInput, ClinicalExtractionResult, MessageType
from app.modules.ai.services import (
    AIExtractionError,
    AIModuleError,
    AIProviderError,
    AIProviderNotConfiguredError,
    BaseAIProvider,
    GeminiProvider,
)

__all__ = [
    "AIMessageInput",
    "MessageType",
    "ClinicalExtractionResult",
    "BaseAIProvider",
    "GeminiProvider",
    "ClinicalExtractionPipeline",
    "AIModuleError",
    "AIProviderError",
    "AIProviderNotConfiguredError",
    "AIExtractionError",
]
