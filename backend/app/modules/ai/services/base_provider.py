from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union

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
    async def process_audio(self, audio_url: str) -> ClinicalExtractionResult:
        """
        Processa um arquivo de áudio referenciado e extrai as informações clínicas estruturadas.
        
        :param audio_url: URL ou referência para obtenção do áudio do paciente.
        :return: ClinicalExtractionResult com os dados clínicos extraídos.
        :raises AIProviderError: Em caso de falha de comunicação ou processamento.
        """
        pass
