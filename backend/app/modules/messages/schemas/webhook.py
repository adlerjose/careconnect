from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class EvolutionWebhookPayload(BaseModel):
    model_config = ConfigDict(extra="allow")

    event: str = Field(..., description="Tipo do evento, por exemplo messages.upsert")
    instance: str = Field(..., description="Nome da instância da Evolution API")
    data: dict[str, Any] = Field(..., description="Payload real da mensagem")
