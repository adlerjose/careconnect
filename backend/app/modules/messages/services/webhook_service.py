import logging
from datetime import datetime, timezone
from typing import Any

from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.ai.pipelines.extraction_pipeline import ClinicalExtractionPipeline
from app.modules.ai.schemas.input import AIMessageInput, MessageType
from app.modules.ai.services.exceptions import AIModuleError
from app.modules.messages.models import Message
from app.modules.patients.models import Patient
from app.modules.triage.models import TriageRecord

logger = logging.getLogger(__name__)


def _extract_message(data: dict[str, Any]) -> tuple[str | None, str | None]:
    message = data.get("message") or {}
    if not isinstance(message, dict):
        return "unknown", None
    if "conversation" in message:
        content = message["conversation"]
        return "text", content if isinstance(content, str) else None
    if "extendedTextMessage" in message:
        extended_text = message["extendedTextMessage"]
        if isinstance(extended_text, dict):
            content = extended_text.get("text")
            return "text", content if isinstance(content, str) else None
        return "text", None
    if "audioMessage" in message:
        return "audio", None
    return "unknown", None


async def _process_text_message_with_ai(
    db: AsyncSession, message: Message
) -> None:
    if message.message_type != "text":
        if message.message_type == "audio":
            message.processing_error = "AudioMediaUnavailable"
            await db.commit()
            logger.warning(
                "AI processing skipped for message %s: audio media is not available",
                message.id,
            )
        return

    try:
        ai_input = AIMessageInput(
            message_id=str(message.id),
            patient_id=str(message.patient_id),
            message_type=MessageType.TEXT,
            content=message.content_text,
        )
        result = await ClinicalExtractionPipeline().run(ai_input)
    except (AIModuleError, ValidationError) as exc:
        message.processing_error = type(exc).__name__
        await db.commit()
        logger.error(
            "AI processing failed for message %s (%s)",
            message.id,
            type(exc).__name__,
        )
        return

    db.add(
        TriageRecord(
            patient_id=message.patient_id,
            message_id=message.id,
            clinical_summary=result.clinical_summary,
            extracted_data=result.model_dump(mode="json"),
            confidence=result.confidence,
            requires_human_review=result.requires_human_review,
        )
    )
    message.processed_at = datetime.now(timezone.utc)
    message.processing_error = None
    await db.commit()
    logger.info("AI triage saved for message %s", message.id)


async def process_webhook(db: AsyncSession, payload: dict[str, Any]) -> None:
    """Persist an inbound Evolution message and its patient, idempotently."""
    data = payload.get("data") or {}
    key = data.get("key") or {}
    if not isinstance(key, dict):
        logger.warning("Ignoring WhatsApp webhook with an invalid message key")
        return

    remote_jid = key.get("remoteJid") or ""
    if not isinstance(remote_jid, str):
        logger.warning("Ignoring WhatsApp webhook with an invalid remote JID")
        return
    whatsapp_number = remote_jid.split("@", maxsplit=1)[0].strip()
    wa_message_id = key.get("id")

    if not whatsapp_number:
        logger.warning("Ignoring WhatsApp webhook without a remote number")
        return
    if remote_jid.endswith("@g.us") or remote_jid == "status@broadcast":
        logger.info("Ignoring WhatsApp group or status message")
        return
    if key.get("fromMe"):
        logger.info("Ignoring outbound WhatsApp message")
        return
    if not isinstance(wa_message_id, str) or not wa_message_id.strip():
        logger.warning("Ignoring WhatsApp webhook without a message ID")
        return

    push_name_value = data.get("pushName")
    push_name = (
        push_name_value.strip()
        if isinstance(push_name_value, str)
        else "Paciente Desconhecido"
    )
    if not push_name:
        push_name = "Paciente Desconhecido"

    patient_id = (
        await db.execute(
            insert(Patient)
            .values(name=push_name, whatsapp_number=whatsapp_number)
            .on_conflict_do_nothing(index_elements=[Patient.whatsapp_number])
            .returning(Patient.id)
        )
    ).scalar_one_or_none()

    if patient_id is None:
        patient = (
            await db.execute(
                select(Patient).where(Patient.whatsapp_number == whatsapp_number)
            )
        ).scalar_one()
        patient_id = patient.id

    message_type, content_text = _extract_message(data)
    insert_result = await db.execute(
        insert(Message)
        .values(
            patient_id=patient_id,
            wa_message_id=wa_message_id,
            raw_payload=payload,
            message_type=message_type,
            content_text=content_text,
            processed_at=None,
        )
        .on_conflict_do_nothing(index_elements=[Message.wa_message_id])
        .returning(Message.id)
    )
    message_id = insert_result.scalar_one_or_none()
    await db.commit()

    if message_id is not None:
        logger.info("Saved %s WhatsApp message for patient %s", message_type, whatsapp_number)
        if message_type in {"text", "audio"}:
            message = await db.get(Message, message_id)
            if message is not None:
                await _process_text_message_with_ai(db, message)
    else:
        logger.info("Ignoring duplicate WhatsApp message %s", wa_message_id)
