from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.modules.ai.schemas.clinical import ClinicalExtractionResult
from app.modules.ai.services.exceptions import AIProviderUnavailableError
from app.modules.messages.models import Message
from app.modules.messages.services import webhook_service
from app.modules.triage.models import TriageRecord


@pytest.mark.anyio
async def test_text_message_is_processed_and_triage_is_saved(monkeypatch) -> None:
    message = Message(
        id=uuid4(),
        patient_id=uuid4(),
        message_type="text",
        content_text="Relata dor de cabeça.",
    )
    result = ClinicalExtractionResult(
        symptoms=["dor de cabeça"],
        clinical_summary="Paciente relata dor de cabeça.",
        confidence=0.9,
        requires_human_review=True,
    )
    pipeline = MagicMock()
    pipeline.run = AsyncMock(return_value=result)
    monkeypatch.setattr(
        webhook_service, "ClinicalExtractionPipeline", lambda: pipeline
    )
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()

    await webhook_service._process_text_message_with_ai(db, message)

    pipeline.run.assert_awaited_once()
    ai_input = pipeline.run.await_args.args[0]
    assert ai_input.content == message.content_text
    assert ai_input.message_id == str(message.id)
    triage = db.add.call_args.args[0]
    assert isinstance(triage, TriageRecord)
    assert triage.patient_id == message.patient_id
    assert triage.message_id == message.id
    assert triage.clinical_summary == result.clinical_summary
    assert triage.extracted_data == result.model_dump(mode="json")
    assert triage.requires_human_review is True
    assert message.processed_at is not None
    assert message.processing_error is None
    db.commit.assert_awaited_once()


@pytest.mark.anyio
async def test_ai_failure_is_recorded_without_creating_triage(monkeypatch) -> None:
    message = Message(
        id=uuid4(),
        patient_id=uuid4(),
        message_type="text",
        content_text="Relata dor de cabeça.",
    )
    pipeline = MagicMock()
    pipeline.run = AsyncMock(
        side_effect=AIProviderUnavailableError("provider unavailable")
    )
    monkeypatch.setattr(
        webhook_service, "ClinicalExtractionPipeline", lambda: pipeline
    )
    db = MagicMock()
    db.add = MagicMock()
    db.commit = AsyncMock()

    await webhook_service._process_text_message_with_ai(db, message)

    assert message.processing_error == "AIProviderUnavailableError"
    assert message.processed_at is None
    db.add.assert_not_called()
    db.commit.assert_awaited_once()
