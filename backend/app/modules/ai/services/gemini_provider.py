from typing import Optional
from app.core.config import settings
from app.modules.ai.schemas.clinical import ClinicalExtractionResult
from app.modules.ai.services.base_provider import BaseAIProvider
from app.modules.ai.services.exceptions import AIProviderNotConfiguredError


class GeminiProvider(BaseAIProvider):
    """
    Implementação da fundação do provedor Google Gemini.
    
    Atenção:
    Esta classe estabelece o contrato e a estrutura técnica para o Google Gemini.
    Chamadas reais à API e dependências de SDKs externos não estão ativas nesta etapa,
    sendo objeto de tarefa de integração dedicada posterior.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: Optional[str] = None,
    ) -> None:
        """
        Inicializa o provedor Gemini utilizando as configurações centrais da aplicação.
        """
        self._api_key = api_key or settings.GEMINI_API_KEY
        self._model_name = model_name or settings.GEMINI_MODEL

    @property
    def provider_name(self) -> str:
        return "gemini"

    @property
    def model_name(self) -> str:
        return self._model_name

    def is_configured(self) -> bool:
        """Verifica se há chave de API informada nas configurações."""
        return bool(self._api_key and self._api_key.strip())

    async def process_text(self, text: str) -> ClinicalExtractionResult:
        """
        Estrutura preliminar para processamento de texto via Google Gemini.
        Levanta AIProviderNotConfiguredError informando que a integração real será ativada posteriormente.
        """
        raise AIProviderNotConfiguredError(
            f"O provedor Gemini (modelo '{self._model_name}') ainda não está configurado para execução real. "
            "A integração com a API do Google Gemini será implementada em tarefa dedicada posterior."
        )

    async def process_audio(self, audio_url: str) -> ClinicalExtractionResult:
        """
        Estrutura preliminar para processamento multimodal de áudio via Google Gemini.
        Levanta AIProviderNotConfiguredError informando que a integração real será ativada posteriormente.
        """
        raise AIProviderNotConfiguredError(
            f"O processamento multimodal de áudio via Gemini ainda não está configurado para execução real. "
            "A integração de transcrição e interpretação de áudio será implementada em tarefa dedicada posterior."
        )
