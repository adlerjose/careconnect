"""
Testes automatizados para a funcionalidade de processamento de áudio no módulo de IA.
Cobre todos os 16 cenários exigidos pela especificação arquitetural, utilizando mocks.
"""

import asyncio
import io
import logging
import struct
import wave
from pathlib import Path
from typing import Optional
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.genai import errors, types

from app.modules.ai.pipelines.extraction_pipeline import ClinicalExtractionPipeline
from app.modules.ai.schemas.clinical import ClinicalExtractionResult
from app.modules.ai.schemas.input import AIMessageInput, MessageType
from app.modules.ai.services.audio_validator import (
    MAX_AUDIO_SIZE_BYTES,
    load_audio_from_source,
    sniff_audio_mime_type,
    validate_and_prepare_audio,
)
from app.modules.ai.services.exceptions import (
    AIExtractionError,
    AIModuleError,
    AIProviderAuthenticationError,
    AIProviderBlockedError,
    AIProviderError,
    AIProviderNotConfiguredError,
    AIProviderRateLimitError,
    AIProviderTimeoutError,
    AIProviderUnavailableError,
)
from app.modules.ai.services.gemini_provider import GeminiProvider


def _create_synthetic_wav_bytes(duration_seconds: float = 0.1) -> bytes:
    """Gera um cabeçalho e payload sintético válido de áudio WAV em memória."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        num_frames = int(16000 * duration_seconds)
        wf.writeframes(struct.pack("<h", 0) * num_frames)
    return buf.getvalue()


def _create_mock_response(
    text: str = "",
    finish_reason: Optional[types.FinishReason] = None,
    parsed: Optional[ClinicalExtractionResult] = None,
) -> MagicMock:
    """Cria um objeto de resposta simulada da API do Gemini."""
    resp = MagicMock()
    resp.text = text
    resp.parsed = parsed
    candidate = MagicMock()
    candidate.finish_reason = finish_reason
    resp.candidates = [candidate]
    return resp


# -------------------------------------------------------------------------
# 1. Processamento de áudio bem-sucedido
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_processing_success():
    """Valida extração bem-sucedida de áudio gerando ClinicalExtractionResult válido."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_resp = _create_mock_response(
        text='{"symptoms": ["dor de garganta", "febre"], "duration": "3 dias", "medications": ["paracetamol 750mg"], "clinical_summary": "Paciente relata febre e dor de garganta há 3 dias.", "confidence": 0.92, "requires_human_review": false}'
    )
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    provider._client = mock_client

    message = AIMessageInput(
        message_id="msg-aud-001",
        patient_id="patient-aud-001",
        message_type=MessageType.AUDIO,
        audio_bytes=wav_bytes,
        mime_type="audio/wav",
    )

    result = await provider.process_audio(message)
    assert isinstance(result, ClinicalExtractionResult)
    assert result.symptoms == ["dor de garganta", "febre"]
    assert result.duration == "3 dias"
    assert result.medications == ["paracetamol 750mg"]
    assert result.confidence == 0.92
    assert result.requires_human_review is True  # Forçado pela salvaguarda


# -------------------------------------------------------------------------
# 2. Áudio vazio
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_empty_audio_raises_extraction_error():
    """Rejeita áudios com 0 bytes ou sem conteúdo sonoro."""
    provider = GeminiProvider(api_key="fake-test-key")

    with pytest.raises(AIExtractionError) as exc_info:
        await provider.process_audio(b"")
    assert "vazio" in str(exc_info.value).lower()


# -------------------------------------------------------------------------
# 3. Formato não suportado
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_unsupported_audio_format_rejected():
    """Rejeita arquivos que não correspondam aos formatos suportados (ex: PDF ou binário genérico)."""
    provider = GeminiProvider(api_key="fake-test-key")

    with pytest.raises(AIExtractionError) as exc_info:
        await provider.process_audio(b"%PDF-1.4 header fake data")
    assert "não é um áudio válido" in str(exc_info.value) or "não suportado" in str(exc_info.value)


# -------------------------------------------------------------------------
# 4. MIME type inválido
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_invalid_mime_type_rejected():
    """Rejeita declarações de MIME type não suportadas (ex: application/json ou video/mp4)."""
    provider = GeminiProvider(api_key="fake-test-key")

    with pytest.raises(AIExtractionError) as exc_info:
        await provider.process_audio(b"fake unknown binary data", mime_type="video/avi")
    assert "não suportado" in str(exc_info.value).lower()


# -------------------------------------------------------------------------
# 5. Resposta vazia do Gemini
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_empty_response_from_gemini():
    """Garante que resposta vazia do Gemini levante AIExtractionError."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(return_value=_create_mock_response(text=""))
    provider._client = mock_client

    with pytest.raises(AIExtractionError) as exc_info:
        await provider.process_audio(wav_bytes)
    assert "resposta textual vazia" in str(exc_info.value)


# -------------------------------------------------------------------------
# 6. JSON inválido retornado pelo Gemini
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_invalid_json_raises_extraction_error():
    """Garante que JSON malformado gere AIExtractionError."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_create_mock_response(text="{invalid_json: true,")
    )
    provider._client = mock_client

    with pytest.raises(AIExtractionError) as exc_info:
        await provider.process_audio(wav_bytes)
    assert "Formato de resposta" in str(exc_info.value) or "não atende ao schema" in str(exc_info.value)


# -------------------------------------------------------------------------
# 7. Resposta incompatível com ClinicalExtractionResult
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_schema_mismatch_raises_extraction_error():
    """Garante que resposta fora do schema gere AIExtractionError."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_create_mock_response(text='{"symptoms": "não é uma lista"}')
    )
    provider._client = mock_client

    with pytest.raises(AIExtractionError) as exc_info:
        await provider.process_audio(wav_bytes)
    assert "não atende ao schema" in str(exc_info.value)


# -------------------------------------------------------------------------
# 8. Timeout
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_timeout_raises_timeout_error():
    """Garante que timeout seja mapeado para AIProviderTimeoutError."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key", timeout=0.01)

    mock_client = MagicMock()

    async def slow_generate(*args, **kwargs):
        await asyncio.sleep(0.1)
        return _create_mock_response(text='{"symptoms": []}')

    mock_client.aio.models.generate_content = slow_generate
    provider._client = mock_client

    with pytest.raises(AIProviderTimeoutError) as exc_info:
        await provider.process_audio(wav_bytes)
    assert "Tempo limite" in str(exc_info.value)


# -------------------------------------------------------------------------
# 9. Erro 503 (Service Unavailable)
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_service_unavailable_error():
    """Garante que HTTP 503 seja mapeado para AIProviderUnavailableError."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    api_err = errors.APIError(code=503, response_json={"error": "UNAVAILABLE"})
    mock_client.aio.models.generate_content = AsyncMock(side_effect=api_err)
    provider._client = mock_client

    with pytest.raises(AIProviderUnavailableError):
        await provider.process_audio(wav_bytes)


# -------------------------------------------------------------------------
# 10. Erro 429 (Rate Limit)
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_rate_limit_error():
    """Garante que HTTP 429 seja mapeado para AIProviderRateLimitError."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    api_err = errors.APIError(code=429, response_json={"error": "RESOURCE_EXHAUSTED"})
    mock_client.aio.models.generate_content = AsyncMock(side_effect=api_err)
    provider._client = mock_client

    with pytest.raises(AIProviderRateLimitError):
        await provider.process_audio(wav_bytes)


# -------------------------------------------------------------------------
# 11. Erro de autenticação (401/403)
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_authentication_error():
    """Garante que HTTP 401/403 seja mapeado para AIProviderAuthenticationError."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-invalid-key")

    mock_client = MagicMock()
    api_err = errors.APIError(code=401, response_json={"error": "API_KEY_INVALID"})
    mock_client.aio.models.generate_content = AsyncMock(side_effect=api_err)
    provider._client = mock_client

    with pytest.raises(AIProviderAuthenticationError):
        await provider.process_audio(wav_bytes)


# -------------------------------------------------------------------------
# 12. Bloqueio por Safety
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_safety_block_raises_blocked_error():
    """Garante que bloqueio de segurança levante AIProviderBlockedError."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_create_mock_response(text="", finish_reason=types.FinishReason.SAFETY)
    )
    provider._client = mock_client

    with pytest.raises(AIProviderBlockedError) as exc_info:
        await provider.process_audio(wav_bytes)
    assert "bloqueada por políticas de segurança" in str(exc_info.value)


# -------------------------------------------------------------------------
# 13. Falha no processamento (não configurado / tipo incorreto / limite tamanho / SSRF)
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_processing_unconfigured_provider():
    """Garante erro de provedor não configurado quando API Key não existe."""
    provider = GeminiProvider(api_key="")
    with pytest.raises(AIProviderNotConfiguredError):
        await provider.process_audio(b"RIFF\x24\x00\x00\x00WAVEfmt ")


@pytest.mark.anyio
async def test_audio_processing_rejects_text_message_type():
    """Garante que passar mensagem do tipo TEXT para process_audio seja rejeitado."""
    provider = GeminiProvider(api_key="fake-key")
    message = AIMessageInput(
        message_id="msg-err-001",
        patient_id="pat-err-001",
        message_type=MessageType.TEXT,
        content="Texto incorreto",
    )
    with pytest.raises(AIModuleError) as exc_info:
        await provider.process_audio(message)
    assert "Esperado AUDIO" in str(exc_info.value)


@pytest.mark.anyio
async def test_audio_processing_rejects_oversized_audio():
    """Garante que arquivos com mais de 20MB sejam rejeitados preventivamente."""
    provider = GeminiProvider(api_key="fake-key")
    huge_data = b"OggS" + b"\x00" * (MAX_AUDIO_SIZE_BYTES + 10)
    with pytest.raises(AIExtractionError) as exc_info:
        await provider.process_audio(huge_data)
    assert "excede o limite máximo permitido" in str(exc_info.value)


@pytest.mark.anyio
async def test_audio_processing_blocks_remote_url_ssrf():
    """Garante bloqueio ativo de SSRF contra URLs remotas."""
    provider = GeminiProvider(api_key="fake-key")
    with pytest.raises(AIExtractionError) as exc_info:
        await provider.process_audio(audio_url="https://evil.internal.service/leak.ogg")
    assert "SSRF" in str(exc_info.value)


# -------------------------------------------------------------------------
# 14. Garantia de requires_human_review=True
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_requires_human_review_enforced():
    """Mesmo se o Gemini retornar requires_human_review=False, a aplicação deve forçar True."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_resp = _create_mock_response(
        text='{"symptoms": [], "duration": null, "medications": [], "clinical_summary": "Sem queixas", "confidence": 0.99, "requires_human_review": false}'
    )
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    provider._client = mock_client

    result = await provider.process_audio(wav_bytes)
    assert result.requires_human_review is True


# -------------------------------------------------------------------------
# 15. Garantia de que identificadores não são enviados ao Gemini
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_identifiers_not_leaked_to_gemini():
    """Garante que patient_id e message_id nunca sejam passados na chamada ao SDK."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_resp = _create_mock_response(
        text='{"symptoms": ["tosse"], "confidence": 0.88, "requires_human_review": true}'
    )
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    provider._client = mock_client

    message = AIMessageInput(
        message_id="super-secret-msg-id-777",
        patient_id="super-secret-patient-id-999",
        message_type=MessageType.AUDIO,
        audio_bytes=wav_bytes,
        mime_type="audio/wav",
    )

    await provider.process_audio(message)

    call_args = mock_client.aio.models.generate_content.call_args
    assert call_args is not None
    contents = call_args.kwargs.get("contents") or call_args.args[1]

    # Verifica que os IDs não constam em nenhum conteúdo enviado
    contents_repr = str(contents)
    assert "super-secret-msg-id-777" not in contents_repr
    assert "super-secret-patient-id-999" not in contents_repr


# -------------------------------------------------------------------------
# 16. Garantia de que dados clínicos e bytes não são registrados em logs
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_clinical_data_not_in_logs(caplog):
    """Garante que bytes de áudio, transcrições e sintomas não vazem nos logs do sistema."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_resp = _create_mock_response(
        text='{"symptoms": ["sensibilidade abdominal aguda"], "clinical_summary": "Transcrição ultra confidencial de cirurgia", "confidence": 0.9}'
    )
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    provider._client = mock_client

    with caplog.at_level(logging.DEBUG):
        await provider.process_audio(wav_bytes)

    captured_text = caplog.text
    # Assegura que o resumo confidencial ou termos clínicos não vazem nos logs do provider
    assert "Transcrição ultra confidencial" not in captured_text
    assert "sensibilidade abdominal aguda" not in captured_text


# -------------------------------------------------------------------------
# 17. Pipeline Audio Routing Integration Test
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_pipeline_routes_audio_message():
    """Valida que o ClinicalExtractionPipeline encaminha mensagens do tipo AUDIO para process_audio."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_resp = _create_mock_response(
        text='{"symptoms": ["dor de dente"], "confidence": 0.85, "requires_human_review": true}'
    )
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    provider._client = mock_client

    pipeline = ClinicalExtractionPipeline(provider=provider)
    message = AIMessageInput(
        message_id="pipe-aud-001",
        patient_id="pipe-pat-001",
        message_type=MessageType.AUDIO,
        audio_bytes=wav_bytes,
        mime_type="audio/wav",
    )

    result = await pipeline.run(message)
    assert result.symptoms == ["dor de dente"]
    assert result.requires_human_review is True


# -------------------------------------------------------------------------
# 18. Semântica: Áudio sem fala ou silencioso com calibração de confiança
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_silent_or_no_speech_calibrates_confidence_to_zero():
    """
    Garante que quando o modelo reportar que o áudio é inaudível/vazio/silencioso,
    a confiança clínica seja calibrada para 0.0 (confiança nula), mesmo se o modelo
    retornar confiança 1.0 (que reflete certeza na ausência de sinal, mas é clinicamente enganosa).
    """
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_resp = _create_mock_response(
        text='{"symptoms": [], "duration": null, "medications": [], "clinical_summary": "O áudio está vazio ou inaudível, não contendo nenhum relato clínico do paciente.", "confidence": 1.0, "requires_human_review": true}'
    )
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    provider._client = mock_client

    result = await provider.process_audio(wav_bytes)

    assert result.symptoms == []
    assert result.medications == []
    assert result.duration is None
    assert result.confidence == 0.0  # Calibrado para zero
    assert result.requires_human_review is True


# -------------------------------------------------------------------------
# 19. Semântica: Áudio com ruído intenso ou incompreensível
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_unintelligible_or_intense_noise_calibrates_confidence_to_zero():
    """Garante que áudio incompreensível por ruído excessivo resulte em confiança nula (0.0)."""
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_resp = _create_mock_response(
        text='{"symptoms": [], "duration": null, "medications": [], "clinical_summary": "Áudio com ruído excessivo de tráfego, fala incompreensível.", "confidence": 0.85, "requires_human_review": true}'
    )
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    provider._client = mock_client

    result = await provider.process_audio(wav_bytes)

    assert result.symptoms == []
    assert result.confidence == 0.0  # Calibrado para zero
    assert result.requires_human_review is True


# -------------------------------------------------------------------------
# 20. Semântica: Áudio nítido com ausência de queixas clínicas
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_clear_speech_without_complaints_preserves_confidence():
    """
    Garante que fala nítida informando que o paciente está bem preserve a confiança do modelo,
    mas mantenha obrigatoriamente requires_human_review=True (sem presumir alta segurança clínica).
    """
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_resp = _create_mock_response(
        text='{"symptoms": [], "duration": null, "medications": [], "clinical_summary": "Paciente relata que está se sentindo muito bem e não apresenta qualquer desconforto.", "confidence": 0.95, "requires_human_review": true}'
    )
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    provider._client = mock_client

    result = await provider.process_audio(wav_bytes)

    assert result.symptoms == []
    assert result.confidence == 0.95  # Preservado pois o áudio não foi inaudível
    assert result.requires_human_review is True


# -------------------------------------------------------------------------
# 21. Semântica: Áudio parcialmente audível / fala incompleta
# -------------------------------------------------------------------------
@pytest.mark.anyio
async def test_audio_partially_audible_incomplete_speech():
    """
    Garante que relatos parcialmente compreensíveis com sintomas parciais preservem
    a confiança intermediária estimada e imponham revisão humana.
    """
    wav_bytes = _create_synthetic_wav_bytes()
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_resp = _create_mock_response(
        text='{"symptoms": ["dor de cabeça"], "duration": null, "medications": [], "clinical_summary": "Paciente relata dor de cabeça, porém trecho final da fala foi cortado por estática.", "confidence": 0.40, "requires_human_review": true}'
    )
    mock_client.aio.models.generate_content = AsyncMock(return_value=mock_resp)
    provider._client = mock_client

    result = await provider.process_audio(wav_bytes)

    assert result.symptoms == ["dor de cabeça"]
    assert result.confidence == 0.40
    assert result.requires_human_review is True
