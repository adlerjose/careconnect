"""Templates de prompts e engenharia de instruções para o modelo de linguagem."""

from app.modules.ai.prompts.templates import (
    AUDIO_EXTRACTION_USER_PROMPT,
    SYSTEM_AUDIO_CLINICAL_EXTRACTION_PROMPT,
    SYSTEM_CLINICAL_EXTRACTION_PROMPT,
)

__all__ = [
    "SYSTEM_CLINICAL_EXTRACTION_PROMPT",
    "SYSTEM_AUDIO_CLINICAL_EXTRACTION_PROMPT",
    "AUDIO_EXTRACTION_USER_PROMPT",
]
