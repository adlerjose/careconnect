from enum import Enum
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class MessageType(str, Enum):
    """Tipos de mensagens suportados inicialmente pelo módulo de IA."""
    TEXT = "TEXT"
    AUDIO = "AUDIO"


class AIMessageInput(BaseModel):
    """
    Contrato de entrada para processamento de mensagens pelo módulo de IA.
    Representa o payload recebido e normalizado a partir dos webhooks da Evolution API.
    """
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid",
        use_enum_values=True,
    )

    message_id: str = Field(
        ...,
        min_length=1,
        description="Identificador único da mensagem no sistema ou gateway de mensageria.",
        examples=["msg-wpp-20261119-001"],
    )
    patient_id: str = Field(
        ...,
        min_length=1,
        description="Identificador único do paciente para correlação clínica.",
        examples=["patient-uuid-1234"],
    )
    message_type: MessageType = Field(
        ...,
        description="Tipo da mensagem recebida: TEXT ou AUDIO.",
        examples=[MessageType.TEXT],
    )
    content: Optional[str] = Field(
        default=None,
        description="Conteúdo textual bruto relatado pelo paciente.",
        examples=["Estou com dor de cabeça forte há 2 dias e tomei dipirona."],
    )
    audio_url: Optional[str] = Field(
        default=None,
        description="Referência de identificação ou caminho do arquivo de áudio.",
        examples=["https://storage.careconnect.local/audios/patient-1234-msg-001.ogg"],
    )
    audio_bytes: Optional[bytes] = Field(
        default=None,
        description="Bytes brutos do arquivo de áudio recebido e validado previamente pela camada de backend.",
    )
    mime_type: Optional[str] = Field(
        default=None,
        description="MIME type informado ou detectado do arquivo de áudio (ex: 'audio/ogg', 'audio/mp3', 'audio/wav').",
    )

    @field_validator("message_id", "patient_id")
    @classmethod
    def validate_non_blank_identifiers(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("Identificadores não podem ser vazios ou constituídos apenas por espaços.")
        return value.strip()

    @model_validator(mode="after")
    def validate_message_consistency(self) -> "AIMessageInput":
        """
        Valida a consistência entre o message_type e a presença dos dados necessários:
        - TEXT: exige 'content' preenchido.
        - AUDIO: exige 'audio_url' ou 'audio_bytes' preenchido.
        Não exige ambos simultaneamente.
        """
        if self.message_type == MessageType.TEXT:
            if not self.content or not self.content.strip():
                raise ValueError(
                    "Mensagens do tipo TEXT exigem o preenchimento obrigatório e não vazio do campo 'content'."
                )

        elif self.message_type == MessageType.AUDIO:
            has_url = bool(self.audio_url and self.audio_url.strip())
            has_bytes = bool(self.audio_bytes and len(self.audio_bytes) > 0)
            if not has_url and not has_bytes:
                raise ValueError(
                    "Mensagens do tipo AUDIO exigem o preenchimento obrigatório de 'audio_url' ou 'audio_bytes'."
                )

        return self
