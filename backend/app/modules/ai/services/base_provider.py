from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

if TYPE_CHECKING:
    from app.modules.ai.schemas.input import AIMessageInput

from app.modules.ai.schemas.clinical import ClinicalExtractionResult


class BaseAIProvider(ABC):
    """
    Interface abstrata para provedores de Inteligência Artificial.
    
    Desacopla as regras de negócio e os pipelines da aplicação de SDKs específicos,
    permitindo alternar ou plugar novos provedores (Google Gemini, OpenAI, Claude, modelos locais)
    sem impacto no restante do sistema.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Identificador textual do provedor de IA (ex: 'gemini', 'openai')."""
        pass

    @abstractmethod
    def is_configured(self) -> bool:
        """Indica se o provedor possui todas as credenciais e configurações necessárias para execução."""
        pass

    @abstractmethod
    async def process_text(self, text: Union["AIMessageInput", str]) -> ClinicalExtractionResult:
        """
        Processa um conteúdo textual ou contrato AIMessageInput e extrai as informações clínicas estruturadas.
        
        :param text: Mensagem textual enviada pelo paciente ou instância de AIMessageInput.
        :return: ClinicalExtractionResult com os dados clínicos extraídos.
        :raises AIProviderError: Em caso de falha de comunicação ou processamento.
        :raises AIExtractionError: Em caso de resposta inválida ou falha de estruturação.
        """
        pass

    @abstractmethod
    async def process_audio(
        self,
        audio: Optional[Union["AIMessageInput", bytes, str, Path]] = None,
        mime_type: Optional[str] = None,
        *,
        audio_url: Optional[str] = None,
    ) -> ClinicalExtractionResult:
        """
        Processa um arquivo ou conteúdo binário de áudio e extrai as informações clínicas estruturadas.
        
        :param audio: Instância de AIMessageInput, bytes brutos, caminho de arquivo local (str ou Path).
        :param mime_type: MIME type do áudio (ex: 'audio/ogg', 'audio/mp3', 'audio/wav').
        :param audio_url: Parâmetro nomeado de compatibilidade para referências locais de áudio.
        :return: ClinicalExtractionResult com os dados clínicos extraídos.
        :raises AIProviderError: Em caso de falha de comunicação ou processamento.
        :raises AIExtractionError: Em caso de áudio vazio, formato inválido ou falha de estruturação.
        """
        pass
