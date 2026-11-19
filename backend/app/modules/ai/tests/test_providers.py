import asyncio
from unittest.mock import AsyncMock, MagicMock
import pytest
from google.genai import errors, types

from app.modules.ai.prompts.templates import SYSTEM_CLINICAL_EXTRACTION_PROMPT
from app.modules.ai.schemas.clinical import ClinicalExtractionResult
from app.modules.ai.schemas.input import AIMessageInput, MessageType
from app.modules.ai.services.base_provider import BaseAIProvider
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


class ConcreteMockProvider(BaseAIProvider):
    """Implementação mock para testar a aderência à interface BaseAIProvider."""

    @property
    def provider_name(self) -> str:
        return "mock_provider"

    def is_configured(self) -> bool:
        return True

    async def process_text(self, text) -> ClinicalExtractionResult:
        content = text.content if isinstance(text, AIMessageInput) else text
        return ClinicalExtractionResult(
            symptoms=["tosse seca sintética"],
            clinical_summary=f"Mock text: {content}",
            confidence=0.9,
            requires_human_review=True,
        )

    async def process_audio(self, audio_url: str) -> ClinicalExtractionResult:
        return ClinicalExtractionResult(
            symptoms=["dor de garganta sintética"],
            clinical_summary=f"Mock audio from {audio_url}",
            confidence=0.85,
            requires_human_review=True,
        )


def _create_mock_response(
    text: str,
    finish_reason: types.FinishReason = types.FinishReason.STOP,
    parsed: object = None,
) -> MagicMock:
    """Helper para criar objetos de resposta mock compatíveis com o SDK google-genai."""
    mock_resp = MagicMock()
    mock_resp.text = text
    mock_resp.parsed = parsed

    candidate = MagicMock()
    candidate.finish_reason = finish_reason
    mock_resp.candidates = [candidate]
    return mock_resp


# ==============================================================================
# 1. Interface BaseAIProvider
# ==============================================================================

def test_base_provider_cannot_be_instantiated():
    """Garante que a classe abstrata BaseAIProvider não possa ser instanciada diretamente."""
    with pytest.raises(TypeError):
        BaseAIProvider()  # type: ignore


@pytest.mark.anyio
async def test_concrete_mock_provider_implements_interface():
    """Valida o funcionamento de uma implementação concreta da interface abstrata."""
    provider = ConcreteMockProvider()
    assert provider.provider_name == "mock_provider"
    assert provider.is_configured() is True

    text_result = await provider.process_text("Relato de teste sintético")
    assert text_result.symptoms == ["tosse seca sintética"]
    assert text_result.confidence == 0.9

    audio_result = await provider.process_audio("https://mock.storage/audio.ogg")
    assert audio_result.symptoms == ["dor de garganta sintética"]
    assert audio_result.confidence == 0.85


# ==============================================================================
# 2. Inicialização, Metadados e Ausência de API Key
# ==============================================================================

def test_gemini_provider_initialization_and_metadata():
    """Valida propriedades iniciais, modelo e timeout do GeminiProvider."""
    provider = GeminiProvider(
        api_key="synthetic_fake_key_123",
        model_name="gemini-3.5-flash-lite",
        timeout=15.0,
    )
    assert provider.provider_name == "gemini"
    assert provider.model_name == "gemini-3.5-flash-lite"
    assert provider.timeout == 15.0
    assert provider.is_configured() is True


def test_gemini_provider_unconfigured_when_no_api_key():
    """Valida que o provedor acusa não configurado quando a chave é vazia."""
    provider = GeminiProvider(api_key="", model_name="gemini-3.5-flash-lite")
    assert provider.is_configured() is False

    with pytest.raises(AIProviderNotConfiguredError) as exc_info:
        provider._get_client()
    assert "GEMINI_API_KEY não foi definida" in str(exc_info.value)


@pytest.mark.anyio
async def test_gemini_provider_process_text_unconfigured_raises_error():
    """Garante que chamar process_text sem configuração levanta AIProviderNotConfiguredError."""
    provider = GeminiProvider(api_key="")
    with pytest.raises(AIProviderNotConfiguredError):
        await provider.process_text("Relato de sintoma")


# ==============================================================================
# 3. Processamento de Texto e Structured Outputs
# ==============================================================================

@pytest.mark.anyio
async def test_gemini_process_text_success_with_valid_response():
    """Valida extração clínica textual com resposta válida do Gemini."""
    provider = GeminiProvider(api_key="fake-test-key", model_name="gemini-3.5-flash-lite")

    mock_client = MagicMock()
    mock_generate = AsyncMock()
    mock_client.aio.models.generate_content = mock_generate
    provider._client = mock_client

    json_payload = (
        '{"symptoms": ["cefaleia intensa", "febre"], '
        '"duration": "2 dias", '
        '"medications": ["dipirona 500mg"], '
        '"clinical_summary": "Paciente relata cefaleia e febre há 2 dias com uso de dipirona.", '
        '"confidence": 0.92, '
        '"requires_human_review": false}'
    )
    mock_generate.return_value = _create_mock_response(text=json_payload)

    result = await provider.process_text("Estou com dor de cabeça forte e febre há 2 dias. Tomei dipirona 500mg.")

    assert isinstance(result, ClinicalExtractionResult)
    assert result.symptoms == ["cefaleia intensa", "febre"]
    assert result.duration == "2 dias"
    assert result.medications == ["dipirona 500mg"]
    assert result.confidence == 0.92
    # Regra de Segurança do MVP: requires_human_review deve ser forçado para True
    assert result.requires_human_review is True

    # Validação do envio dos parâmetros e structured outputs
    mock_generate.assert_awaited_once()
    _, kwargs = mock_generate.call_args
    assert kwargs["model"] == "gemini-3.5-flash-lite"
    assert kwargs["contents"] == "Estou com dor de cabeça forte e febre há 2 dias. Tomei dipirona 500mg."

    config = kwargs["config"]
    assert isinstance(config, types.GenerateContentConfig)
    assert config.response_mime_type == "application/json"
    assert config.response_schema == ClinicalExtractionResult
    assert config.system_instruction == SYSTEM_CLINICAL_EXTRACTION_PROMPT


@pytest.mark.anyio
async def test_gemini_process_text_with_aimessageinput_does_not_leak_identifiers():
    """Garante que patient_id e message_id NUNCA sejam enviados ao Gemini."""
    provider = GeminiProvider(api_key="fake-test-key")

    mock_client = MagicMock()
    mock_generate = AsyncMock()
    mock_client.aio.models.generate_content = mock_generate
    provider._client = mock_client

    json_payload = '{"symptoms": ["náusea"], "requires_human_review": false}'
    mock_generate.return_value = _create_mock_response(text=json_payload)

    message = AIMessageInput(
        message_id="secret-msg-id-9999",
        patient_id="secret-patient-id-8888",
        message_type=MessageType.TEXT,
        content="Paciente relata náusea após o almoço.",
    )

    result = await provider.process_text(message)

    assert result.symptoms == ["náusea"]
    assert result.requires_human_review is True

    _, kwargs = mock_generate.call_args
    contents_sent = kwargs["contents"]
    # Assegura ausência de identificadores pessoais
    assert "secret-msg-id-9999" not in contents_sent
    assert "secret-patient-id-8888" not in contents_sent
    assert contents_sent == "Paciente relata náusea após o almoço."


@pytest.mark.anyio
async def test_gemini_rejects_non_text_message_type():
    """Garante que process_text rejeite mensagens que não sejam do tipo TEXT."""
    provider = GeminiProvider(api_key="fake-test-key")
    audio_message = AIMessageInput(
        message_id="msg-audio-001",
        patient_id="pat-001",
        message_type=MessageType.AUDIO,
        audio_url="https://audio.local/test.ogg",
    )

    with pytest.raises(AIModuleError) as exc_info:
        await provider.process_text(audio_message)
    assert "Esperado TEXT" in str(exc_info.value)


@pytest.mark.anyio
async def test_gemini_rejects_empty_content():
    """Rejeita conteúdos vazios com AIExtractionError."""
    provider = GeminiProvider(api_key="fake-test-key")
    with pytest.raises(AIExtractionError):
        await provider.process_text("   ")


# ==============================================================================
# 4. Tratamento de Erros, Respostas Anômalas e Bloqueios
# ==============================================================================

@pytest.mark.anyio
async def test_gemini_empty_response_raises_extraction_error():
    """Garante que respostas textuais vazias do modelo gerem AIExtractionError."""
    provider = GeminiProvider(api_key="fake-test-key")
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_create_mock_response(text="")
    )
    provider._client = mock_client

    with pytest.raises(AIExtractionError) as exc_info:
        await provider.process_text("Relato do paciente")
    assert "resposta textual vazia" in str(exc_info.value)


@pytest.mark.anyio
async def test_gemini_invalid_json_raises_extraction_error():
    """Garante que retorno não-JSON gere AIExtractionError."""
    provider = GeminiProvider(api_key="fake-test-key")
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_create_mock_response(text="Texto livre sem formatação JSON")
    )
    provider._client = mock_client

    with pytest.raises(AIExtractionError) as exc_info:
        await provider.process_text("Relato do paciente")
    assert "Formato de resposta" in str(exc_info.value) or "não atende ao schema" in str(exc_info.value)


@pytest.mark.anyio
async def test_gemini_schema_mismatch_raises_extraction_error():
    """Garante que JSON incompatível com ClinicalExtractionResult gere AIExtractionError."""
    provider = GeminiProvider(api_key="fake-test-key")
    mock_client = MagicMock()
    # confidence inválida (> 1.0)
    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_create_mock_response(text='{"symptoms": ["tosse"], "confidence": 5.0}')
    )
    provider._client = mock_client

    with pytest.raises(AIExtractionError) as exc_info:
        await provider.process_text("Relato do paciente")
    assert "não atende ao schema" in str(exc_info.value)


@pytest.mark.anyio
async def test_gemini_safety_block_raises_blocked_error():
    """Garante que bloqueios de segurança levantem AIProviderBlockedError."""
    provider = GeminiProvider(api_key="fake-test-key")
    mock_client = MagicMock()
    mock_client.aio.models.generate_content = AsyncMock(
        return_value=_create_mock_response(text="", finish_reason=types.FinishReason.SAFETY)
    )
    provider._client = mock_client

    with pytest.raises(AIProviderBlockedError) as exc_info:
        await provider.process_text("Relato sensível")
    assert "bloqueada por políticas de segurança" in str(exc_info.value)


@pytest.mark.anyio
async def test_gemini_timeout_raises_timeout_error():
    """Garante que requisições que excedam o timeout levantem AIProviderTimeoutError."""
    provider = GeminiProvider(api_key="fake-test-key", timeout=0.01)

    mock_client = MagicMock()

    async def slow_generate(*args, **kwargs):
        await asyncio.sleep(0.1)
        return _create_mock_response(text='{"symptoms": []}')

    mock_client.aio.models.generate_content = slow_generate
    provider._client = mock_client

    with pytest.raises(AIProviderTimeoutError) as exc_info:
        await provider.process_text("Relato do paciente")
    assert "Tempo limite" in str(exc_info.value)


@pytest.mark.anyio
async def test_gemini_authentication_error_mapping():
    """Garante que erro HTTP 401/403 seja mapeado para AIProviderAuthenticationError."""
    provider = GeminiProvider(api_key="fake-invalid-key")
    mock_client = MagicMock()

    api_err = errors.APIError(code=401, response_json={"error": "API_KEY_INVALID"})
    mock_client.aio.models.generate_content = AsyncMock(side_effect=api_err)
    provider._client = mock_client

    with pytest.raises(AIProviderAuthenticationError):
        await provider.process_text("Relato do paciente")


@pytest.mark.anyio
async def test_gemini_rate_limit_error_mapping():
    """Garante que erro HTTP 429 seja mapeado para AIProviderRateLimitError."""
    provider = GeminiProvider(api_key="fake-key")
    mock_client = MagicMock()

    api_err = errors.APIError(code=429, response_json={"error": "RESOURCE_EXHAUSTED"})
    mock_client.aio.models.generate_content = AsyncMock(side_effect=api_err)
    provider._client = mock_client

    with pytest.raises(AIProviderRateLimitError):
        await provider.process_text("Relato do paciente")


@pytest.mark.anyio
async def test_gemini_service_unavailable_error_mapping():
    """Garante que erro HTTP 503 seja mapeado para AIProviderUnavailableError."""
    provider = GeminiProvider(api_key="fake-key")
    mock_client = MagicMock()

    api_err = errors.APIError(code=503, response_json={"error": "UNAVAILABLE"})
    mock_client.aio.models.generate_content = AsyncMock(side_effect=api_err)
    provider._client = mock_client

    with pytest.raises(AIProviderUnavailableError):
        await provider.process_text("Relato do paciente")


@pytest.mark.anyio
async def test_gemini_generic_api_error_mapping():
    """Garante que erro de API desconhecido seja mapeado para AIProviderError."""
    provider = GeminiProvider(api_key="fake-key")
    mock_client = MagicMock()

    api_err = errors.APIError(code=599, response_json={"error": "UNKNOWN"})
    mock_client.aio.models.generate_content = AsyncMock(side_effect=api_err)
    provider._client = mock_client

    with pytest.raises(AIProviderError):
        await provider.process_text("Relato do paciente")


@pytest.mark.anyio
async def test_gemini_process_audio_not_implemented():
    """Garante que o processamento de áudio permaneça sinalizado como não implementado."""
    provider = GeminiProvider(api_key="fake-key")
    with pytest.raises(NotImplementedError) as exc_info:
        await provider.process_audio("https://storage.local/audio.ogg")
    assert "não está ativo nesta versão do MVP" in str(exc_info.value)
