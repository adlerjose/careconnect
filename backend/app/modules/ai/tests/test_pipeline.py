from unittest.mock import AsyncMock, MagicMock
import pytest
from app.modules.ai.pipelines.extraction_pipeline import ClinicalExtractionPipeline
from app.modules.ai.schemas.clinical import ClinicalExtractionResult
from app.modules.ai.schemas.input import AIMessageInput, MessageType
from app.modules.ai.services.base_provider import BaseAIProvider
from app.modules.ai.services.exceptions import AIProviderNotConfiguredError
from app.modules.ai.services.gemini_provider import GeminiProvider


class SyntheticMockProvider(BaseAIProvider):
    """Provedor sintético para validação do pipeline sem chamadas externas."""

    @property
    def provider_name(self) -> str:
        return "synthetic_mock"

    def is_configured(self) -> bool:
        return True

    async def process_text(self, text) -> ClinicalExtractionResult:
        return ClinicalExtractionResult(
            symptoms=["febre sintética"],
            duration="1 dia",
            clinical_summary="Resumo sintético de texto",
            confidence=0.95,
            requires_human_review=True,
        )

    async def process_audio(self, audio_url: str) -> ClinicalExtractionResult:
        return ClinicalExtractionResult(
            symptoms=["coriza sintética"],
            clinical_summary=f"Resumo sintético de áudio ({audio_url})",
            confidence=0.91,
            requires_human_review=True,
        )


@pytest.mark.anyio
async def test_pipeline_dispatches_text_message():
    """Valida que o pipeline despacha mensagens de texto para process_text."""
    pipeline = ClinicalExtractionPipeline(provider=SyntheticMockProvider())
    message = AIMessageInput(
        message_id="msg-pipe-001",
        patient_id="pat-pipe-001",
        message_type=MessageType.TEXT,
        content="Paciente com febre sintética há 1 dia.",
    )

    result = await pipeline.run(message)
    assert result.symptoms == ["febre sintética"]
    assert result.duration == "1 dia"
    assert result.confidence == 0.95
    assert result.requires_human_review is True


@pytest.mark.anyio
async def test_pipeline_dispatches_audio_message():
    """Valida que o pipeline despacha mensagens de áudio para process_audio."""
    pipeline = ClinicalExtractionPipeline(provider=SyntheticMockProvider())
    message = AIMessageInput(
        message_id="msg-pipe-002",
        patient_id="pat-pipe-002",
        message_type=MessageType.AUDIO,
        audio_url="https://mock.storage/audio002.ogg",
    )

    result = await pipeline.run(message)
    assert result.symptoms == ["coriza sintética"]
    assert "audio002.ogg" in (result.clinical_summary or "")
    assert result.confidence == 0.91
    assert result.requires_human_review is True


@pytest.mark.anyio
async def test_pipeline_with_gemini_provider_unconfigured():
    """Valida que o pipeline com o GeminiProvider propaga adequadamente a exceção de não configurado."""
    pipeline = ClinicalExtractionPipeline(provider=GeminiProvider(api_key=""))
    message = AIMessageInput(
        message_id="msg-pipe-003",
        patient_id="pat-pipe-003",
        message_type=MessageType.TEXT,
        content="Mensagem de teste sintética",
    )

    with pytest.raises(AIProviderNotConfiguredError):
        await pipeline.run(message)


@pytest.mark.anyio
async def test_pipeline_with_gemini_provider_success():
    """Valida a execução do pipeline com o GeminiProvider funcional usando mock."""
    gemini_provider = GeminiProvider(api_key="fake-test-key")
    mock_client = MagicMock()
    mock_resp = MagicMock()
    mock_resp.text = '{"symptoms": ["cefaleia"], "duration": "2 dias", "confidence": 0.85, "requires_human_review": false}'
    mock_candidate = MagicMock()
    mock_candidate.finish_reason = None
    mock_resp.candidates = [mock_candidate]
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    gemini_provider._client = mock_client

    pipeline = ClinicalExtractionPipeline(provider=gemini_provider)
    message = AIMessageInput(
        message_id="msg-pipe-004",
        patient_id="pat-pipe-004",
        message_type=MessageType.TEXT,
        content="Estou com dor de cabeça há dois dias.",
    )

    result = await pipeline.run(message)
    assert result.symptoms == ["cefaleia"]
    assert result.duration == "2 dias"
    assert result.requires_human_review is True
