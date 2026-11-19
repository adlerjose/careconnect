from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ClinicalExtractionResult(BaseModel):
    """
    Contrato de saída para extração clínica estruturada a partir de relatos do paciente.
    
    Diretrizes Éticas e Clínicas:
    - Representa estritamente dados relatados pelo paciente.
    - NÃO constitui diagnóstico, prescrição ou parecer médico definitivo.
    - Campos ausentes no relato não devem ser inferidos ou inventados.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        validate_assignment=True,
    )

    symptoms: List[str] = Field(
        default_factory=list,
        description="Lista de sintomas expressamente relatados pelo paciente (sem inferências diagnósticas).",
        examples=[["cefaleia", "febre"]],
    )
    duration: Optional[str] = Field(
        default=None,
        description="Duração ou tempo de evolução dos sintomas conforme informado pelo paciente (ex: '2 dias', 'desde ontem').",
        examples=["2 dias"],
    )
    medications: List[str] = Field(
        default_factory=list,
        description="Medicamentos que o paciente informou estar utilizando ou haver ingerido.",
        examples=[["dipirona 500mg"]],
    )
    clinical_summary: Optional[str] = Field(
        default=None,
        description="Resumo descritivo e objetivo do relato clínico original, preservando a fala do paciente.",
        examples=["Paciente relata dor de cabeça de forte intensidade há 2 dias, fez uso de analgésico sem melhora."],
    )
    confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Grau de certeza ou aderência semântica estimado pelo modelo na extração (intervalo [0.0, 1.0]).",
        examples=[0.85],
    )
    requires_human_review: bool = Field(
        default=False,
        description="Sinalizador de revisão obrigatória por profissional de saúde devido a ambiguidades ou baixa clareza.",
        examples=[False],
    )

    @field_validator("symptoms", "medications")
    @classmethod
    def clean_string_lists(cls, values: List[str]) -> List[str]:
        """Sanitiza listas de sintomas e medicamentos removendo entradas vazias ou duplicadas."""
        cleaned: List[str] = []
        for item in values:
            if isinstance(item, str):
                trimmed = item.strip()
                if trimmed and trimmed not in cleaned:
                    cleaned.append(trimmed)
        return cleaned

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, value: Optional[str]) -> Optional[str]:
        """Garante que strings de duração vazias sejam tratadas como ausência de informação (None)."""
        if value is not None and not value.strip():
            return None
        return value
