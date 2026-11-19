"""Schemas Pydantic para o módulo de Inteligência Artificial."""

from app.modules.ai.schemas.clinical import ClinicalExtractionResult
from app.modules.ai.schemas.input import AIMessageInput, MessageType

__all__ = [
    "AIMessageInput",
    "MessageType",
    "ClinicalExtractionResult",
]
