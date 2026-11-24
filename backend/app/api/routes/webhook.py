import secrets
from typing import Annotated, Any

from fastapi import APIRouter, BackgroundTasks, Header, HTTPException, status

from app.core.config import settings
from app.core.database import AsyncSessionLocal
from app.modules.messages.schemas.webhook import EvolutionWebhookPayload
from app.modules.messages.services.webhook_service import process_webhook

router = APIRouter(prefix="/webhook", tags=["WhatsApp Webhook"])


async def process_webhook_bg(payload: dict[str, Any]) -> None:
    async with AsyncSessionLocal() as db:
        await process_webhook(db, payload)


@router.post("/whatsapp", status_code=status.HTTP_200_OK)
async def receive_whatsapp_webhook(
    payload: EvolutionWebhookPayload,
    background_tasks: BackgroundTasks,
    apikey: Annotated[str | None, Header(alias="apikey")] = None,
) -> dict[str, str]:
    if not settings.EVOLUTION_API_KEY or not apikey or not secrets.compare_digest(
        apikey, settings.EVOLUTION_API_KEY
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Chave de API inválida",
        )

    if payload.event != "messages.upsert":
        return {"status": "ignored", "reason": "Not a message event"}

    background_tasks.add_task(process_webhook_bg, payload.model_dump())
    return {"status": "success", "message": "Webhook received"}
