import pytest
from app.modules.ai.schemas.clinical import ClinicalExtractionResult
from app.modules.ai.services.base_provider import BaseAIProvider
from app.modules.ai.services.exceptions import AIProviderNotConfiguredError
from app.modules.ai.services.gemini_provider import GeminiProvider


class ConcreteMockProvider(BaseAIProvider):
    """Implementação mock para testar a aderência à interface BaseAIProvider."""

    @property
    def provider_name(self) -> str:
        return "mock_provider"

    def is_configured(self) -> bool:
        return True

    async def process_text(self, text: str) -> ClinicalExtractionResult:
        return ClinicalExtractionResult(
            symptoms=["tosse seca sintética"],
            clinical_summary=f"Mock text: {text}",
            confidence=0.9,
        )

    async def process_audio(self, audio_url: str) -> ClinicalExtractionResult:
        return ClinicalExtractionResult(
            symptoms=["dor de garganta sintética"],
            clinical_summary=f"Mock audio from {audio_url}",
            confidence=0.85,
        )


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


def test_gemini_provider_initialization_and_metadata():
    """Valida propriedades iniciais e estado de configuração do GeminiProvider."""
    provider = GeminiProvider(api_key="", model_name="gemini-2.5-flash")
    assert provider.provider_name == "gemini"
    assert provider.model_name == "gemini-2.5-flash"
    assert provider.is_configured() is False

    provider_with_key = GeminiProvider(api_key="synthetic_fake_key_123")
    assert provider_with_key.is_configured() is True


@pytest.mark.anyio
async def test_gemini_provider_methods_raise_not_configured_error():
    """
    Garante que métodos de processamento do GeminiProvider lancem AIProviderNotConfiguredError,
    explicitando que a integração real ainda não está configurada e não executando chamadas de rede.
    """
    provider = GeminiProvider(api_key="", model_name="gemini-2.5-flash")

    with pytest.raises(AIProviderNotConfiguredError) as exc_text:
        await provider.process_text("Texto de paciente sintético")
    assert "ainda não está configurado para execução real" in str(exc_text.value)

    with pytest.raises(AIProviderNotConfiguredError) as exc_audio:
        await provider.process_audio("https://storage.local/audio.ogg")
    assert "ainda não está configurado para execução real" in str(exc_audio.value)
